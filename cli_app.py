"""
TermiPilot Interactive Terminal Interface (TUI).
High-performance developer CLI with Rich formatting, live spinners, tool visualization, and safety gates.
"""
import sys
import os
import io

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Confirm, Prompt

from core.agent import TermiPilotAgent
from core.memory import DatabaseManager

console = Console(legacy_windows=False)


def terminal_approval_handler(command: str, reason: str) -> bool:
    """
    Human-in-the-Loop terminal confirmation callback.
    Prompts the user before executing any moderate or critical command.
    """
    console.print("\n")
    console.print(Panel(
        f"[bold red]⚠️  SECURITY GUARD INTERCEPTION[/bold red]\n\n"
        f"[bold]Reason:[/bold] {reason}\n"
        f"[bold]Target Command:[/bold] [yellow]{command}[/yellow]\n\n"
        f"[dim]TermiPilot blocked automatic execution to prevent unauthorized system modifications.[/dim]",
        title="[bold yellow]Safety Check[/bold yellow]",
        border_style="red"
    ))
    return Confirm.ask("[bold red]Do you authorize execution of this command?[/bold red]", default=False)


def render_banner():
    banner_text = """[bold cyan]
   ______                    _ ____  _ __      __ 
  /_  __/__  _________ ___  (_) __ \(_) /___  / /_
   / / / _ \/ ___/ __ `__ \/ / /_/ / / / __ \/ __/
  / / /  __/ /  / / / / / / / ____/ / / /_/ / /_  
 /_/  \___/_/  /_/ /_/ /_/_/_/   /_/_/\____/\__/  
[/bold cyan]
[bold white]Autonomous AI DevOps & Terminal Copilot[/bold white] | [green]B.Tech Capstone Edition[/green]
[dim]Powered by Groq High-Speed LLM & Guardrailed Tool Execution Bus[/dim]
"""
    console.print(Panel(banner_text, border_style="cyan"))


def display_audit_history(db: DatabaseManager, chat_id: str):
    logs = db.get_audit_logs(chat_id=chat_id, limit=10)
    if not logs:
        console.print("[dim]No tool executions recorded for this session yet.[/dim]")
        return

    table = Table(title="Recent Tool Execution Audit Trail", border_style="blue")
    table.add_column("Tool", style="cyan")
    table.add_column("Command / Args", style="white")
    table.add_column("Risk Level", style="magenta")
    table.add_column("Approved", style="green")
    table.add_column("Latency (ms)", justify="right")

    for log in reversed(logs):
        cmd = log["command"]
        if len(cmd) > 40:
            cmd = cmd[:37] + "..."
        table.add_row(
            log["tool_name"],
            cmd,
            log["risk_level"],
            "✓ Yes" if log["user_approved"] else "✗ No",
            f"{log['duration_ms']:.1f}"
        )
    console.print(table)


def main():
    render_banner()

    db = DatabaseManager()
    chat_id = db.create_chat(username="developer", title="Terminal Session")

    # Initialize agent with terminal approval handler
    try:
        agent = TermiPilotAgent(
            db_manager=db,
            approval_callback=terminal_approval_handler
        )
    except Exception as e:
        console.print(f"[bold red]Initialization Error:[/bold red] {e}")
        console.print("[yellow]Ensure GROQ_API_KEY is configured in your .env file.[/yellow]")
        sys.exit(1)

    console.print(f"[green]✓ Connected to Groq LLM ([bold]{agent.model}[/bold])[/green]")
    console.print(f"[dim]Active Session ID: {chat_id}[/dim]")
    console.print("[dim]Type your task or question. Commands: '/history', '/clear', '/help', 'exit'[/dim]\n")

    while True:
        try:
            cwd_short = os.path.basename(os.getcwd()) or os.getcwd()
            user_input = Prompt.ask(f"[bold blue]termi[/bold blue]:[cyan]~/{cwd_short}[/cyan] [bold]❯[/bold]").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", ":q"]:
                console.print("[bold cyan]Goodbye! TermiPilot session closed.[/bold cyan]")
                break

            if user_input == "/clear":
                console.clear()
                render_banner()
                continue

            if user_input == "/history":
                display_audit_history(db, chat_id)
                continue

            if user_input == "/help":
                console.print(Panel(
                    "- Ask anything: [cyan]'What files are in this repo?'[/cyan]\n"
                    "- DevOps diagnosis: [cyan]'Check if python is installed and print the version'[/cyan]\n"
                    "- Script runner: [cyan]'Calculate prime numbers up to 100 with Python'[/cyan]\n"
                    "- Web tech lookup: [cyan]'Search documentation for FastAPI background tasks'[/cyan]\n"
                    "- Commands: [yellow]/history[/yellow], [yellow]/clear[/yellow], [yellow]exit[/yellow]",
                    title="TermiPilot Help",
                    border_style="blue"
                ))
                continue

            # Status callback to display tool execution live
            def status_hook(event_type: str, tool_name: str, data: dict):
                if event_type == "tool_start":
                    console.print(f"  [yellow]⚡ Running Tool:[/yellow] [bold cyan]{tool_name}[/bold cyan] -> [dim]{data}[/dim]")
                elif event_type == "tool_end":
                    status = data.get("status", "done")
                    color = "green" if status == "success" else "red"
                    console.print(f"  [{color}]✓ Tool completed ({status})[/{color}]")

            with console.status("[bold green]TermiPilot is reasoning & planning...[/bold green]", spinner="dots"):
                result = agent.run_step(
                    chat_id=chat_id,
                    user_message=user_input,
                    status_callback=status_hook
                )

            # Render response markdown
            console.print("\n")
            console.print(Panel(
                Markdown(result["reply"]),
                title=f"[bold green]TermiPilot Assistant[/bold green] [dim]({result['latency_sec']:.2f}s)[/dim]",
                border_style="green"
            ))
            console.print("\n")

        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrupted. Type 'exit' to quit.[/yellow]")
        except Exception as err:
            console.print(f"[bold red]Unexpected Error:[/bold red] {err}")


if __name__ == "__main__":
    main()
