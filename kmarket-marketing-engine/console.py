import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.kmarket_bot import KMarketGrowthBot
from core.easytax_bot import EasyTaxRefundBot
from modules.seo_kmarket import KMarketSEOPusher
from modules.seo_easytax import EasyTaxSEOPusher

console = Console()

def run_cli():
    db_mgr = DBManager()
    supabase_mgr = SupabaseManager(db_mgr)
    
    kmarket_bot = KMarketGrowthBot(db_mgr, supabase_mgr)
    easytax_bot = EasyTaxRefundBot(db_mgr, supabase_mgr)

    while True:
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]🛸 Universal Expat Growth Engine (Dual Autonomous Micro-Bots)[/bold cyan]\n"
            "[bold green]🛒 K-Market 100% 라이프 봇[/bold green]  &  [bold yellow]💰 EasyTax 100% 세무환급 봇[/bold yellow]",
            border_style="cyan"
        ))

        table = Table(title="🎛️ 독립 듀얼 봇 선택 및 작업 메뉴", show_header=True, header_style="bold magenta")
        table.add_column("번호", style="dim", width=6)
        table.add_column("브랜드 및 작업", style="bold")
        table.add_column("설명", style="cyan")

        table.add_row("1", "🛒 K-Market 봇 사이클 즉시 실행", "270개 실물 매물 숏폼, 4장 카드뉴스, 가구 레딧, 0원 나눔 브리핑")
        table.add_row("2", "💰 EasyTax 봇 사이클 즉시 실행", "E-9 90%감면 숏폼, Anti-Ban 세무 카드뉴스, 조특법 레딧, 세무 브리핑")
        table.add_row("3", "🛒 K-Market 구글 SEO 1,105개 색인 핑", "전국 65개 캠퍼스/공단 URL 및 사이트맵 빌드")
        table.add_row("4", "💰 EasyTax 구글 SEO 1,105개 색인 핑", "전국 65개 공단/비자 세무 URL 및 사이트맵 빌드")
        table.add_row("q", "종료", "CLI 콘솔 종료")

        console.print(table)
        choice = Prompt.ask("\n실행할 메뉴 번호를 입력하세요", choices=["1", "2", "3", "4", "q"], default="1")

        if choice == "1":
            console.print("\n[bold green]🛒 K-Market 봇 사이클 가동 중...[/bold green]")
            res = kmarket_bot.run_kmarket_cycle()
            console.print(f"[bold green]결과:[/bold green] {res}")
            Prompt.ask("\n계속하려면 Enter를 누르세요")
        elif choice == "2":
            console.print("\n[bold yellow]💰 EasyTax 봇 사이클 가동 중...[/bold yellow]")
            res = easytax_bot.run_easytax_cycle()
            console.print(f"[bold yellow]결과:[/bold yellow] {res}")
            Prompt.ask("\n계속하려면 Enter를 누르세요")
        elif choice == "3":
            console.print("\n[bold green]🛒 K-Market 구글 색인 빌드 및 핑 전송 중...[/bold green]")
            pusher = KMarketSEOPusher(db_mgr)
            res = pusher.build_and_ping()
            console.print(f"[bold green]결과:[/bold green] {res}")
            Prompt.ask("\n계속하려면 Enter를 누르세요")
        elif choice == "4":
            console.print("\n[bold yellow]💰 EasyTax 구글 색인 빌드 및 핑 전송 중...[/bold yellow]")
            pusher = EasyTaxSEOPusher(db_mgr)
            res = pusher.build_and_ping()
            console.print(f"[bold yellow]결과:[/bold yellow] {res}")
            Prompt.ask("\n계속하려면 Enter를 누르세요")
        elif choice == "q":
            console.print("[dim]CLI 콘솔을 종료합니다.[/dim]")
            break

if __name__ == "__main__":
    run_cli()
