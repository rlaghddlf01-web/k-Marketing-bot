import os, sys, time
from pathlib import Path

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, r'C:\ktrs_marketing_bot\kmarket-marketing-engine')
from dotenv import dotenv_values
from google import genai

env_path = Path(r'C:\ktrs_marketing_bot\kmarket-marketing-engine\.env')
vals = dotenv_values(env_path)

keys_to_test = {
    '유료키 1 (EASYTAX / DEFAULT)': vals.get('GEMINI_PAID_API_KEY') or vals.get('GEMINI_API_KEY'),
    '유료키 2 (KMARKET)': vals.get('GEMINI_API_KEY_KMARKET'),
    '무료키 1 (KMARKET BLOG)': vals.get('GEMINI_FREE_API_KEY_KMARKET'),
    '무료키 2 (EASYTAX BLOG)': vals.get('GEMINI_FREE_API_KEY_EASYTAX'),
    '무료키 3 (EXTRA / COMMON)': vals.get('GEMINI_FREE_API_KEY_EXTRA'),
}

print('=' * 60)
print('🧪 Gemini API 키 4종 응답 테스트 시작')
print('=' * 60 + '\n')

for label, key_val in keys_to_test.items():
    if not key_val:
        print(f'❌ [{label}]: 키가 비어있습니다.\n')
        continue
    masked = key_val[:10] + '...' + key_val[-4:]
    print(f'▶ [{label}] (키: {masked}) 테스트 중...')
    try:
        client = genai.Client(api_key=key_val)
        t0 = time.time()
        res = client.models.generate_content(
            model='gemini-flash-lite-latest',
            contents='Answer in 1 word: Pong'
        )
        elapsed = time.time() - t0
        reply = res.text.strip() if res.text else 'Empty'
        print(f'   ✅ 텍스트(LLM) 응답 성공! ({elapsed:.2f}초): "{reply}"')
    except Exception as e:
        print(f'   ❌ 텍스트(LLM) 응답 실패: {e}')

    if '유료' in label:
        try:
            t0 = time.time()
            img_res = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt='A clean Korean wooden office desk, minimalist, 16:9',
                config=dict(number_of_images=1, output_mime_type='image/jpeg', aspect_ratio='16:9')
            )
            elapsed_img = time.time() - t0
            img_count = len(img_res.generated_images) if img_res and img_res.generated_images else 0
            print(f'   🎨 Imagen 3 이미지 생성 성공! ({elapsed_img:.2f}초, {img_count}장 생성)')
        except Exception as e:
            print(f'   ⚠️ Imagen 3 테스트 실패/미지원: {e}')
    print('')

print('=' * 60)
print('🏁 테스트 완료')
print('=' * 60)