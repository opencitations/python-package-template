#!/usr/bin/env python3

# SPDX-FileCopyrightText: [year] Author Name <author@example.com>
#
# SPDX-License-Identifier: ISC

"""Interactive setup script for the Python package template."""

import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()


def _require_uv() -> None:
    if shutil.which("uv"):
        return
    print("UV is required to run this setup.", file=sys.stderr)
    print("Install it from: https://docs.astral.sh/uv/getting-started/installation/", file=sys.stderr)
    sys.exit(1)


def _install_rich() -> None:
    subprocess.run(
        ["uv", "pip", "install", "-q", "rich"],
        capture_output=True,
        check=True,
    )


def _uninstall_rich() -> None:
    subprocess.run(
        ["uv", "pip", "uninstall", "-y", "rich"],
        capture_output=True,
    )


def validate_package_name(name: str) -> bool:
    pattern = r"^[a-zA-Z][a-zA-Z0-9]*(-[a-zA-Z0-9]+)*$"
    return bool(re.match(pattern, name))


def to_underscore(name: str) -> str:
    return name.replace("-", "_")


def replace_in_file(filepath: Path, replacements: dict[str, str]) -> None:
    content = filepath.read_text()
    for old, new in replacements.items():
        content = content.replace(old, new)
    filepath.write_text(content)


def run_command(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    output = result.stdout + result.stderr
    return result.returncode == 0, output


def main() -> int:  # pragma: no cover
    _require_uv()
    _install_rich()

    # Imported after runtime installation (rich is not a project dependency)
    from rich.console import Console  # type: ignore[reportMissingImports]
    from rich.prompt import Confirm, Prompt  # type: ignore[reportMissingImports]
    from rich.table import Table  # type: ignore[reportMissingImports]

    console = Console()

    def print_header(text: str) -> None:
        console.print()
        console.rule(f"[bold]{text}[/bold]", style="cyan")
        console.print()

    def print_step(text: str) -> None:
        console.print(f"  [cyan]->[/cyan] {text}")

    def print_success(text: str) -> None:
        console.print(f"  [green]\\[OK][/green] {text}")

    def print_error(text: str) -> None:
        console.print(f"  [red]\\[ERROR][/red] {text}", stderr=True)

    def ask_required(label: str) -> str:
        while True:
            value = Prompt.ask(f"[bold]{label}[/bold]").strip()
            if value:
                return value
            console.print("  [yellow]This field is required.[/yellow]")

    print_header("Python package template setup")
    console.print("This script will configure the template for your project.\n")

    while True:
        package_name = Prompt.ask(
            "[bold]Package name[/bold] (e.g., my-awesome-lib)"
        ).strip()
        if not package_name:
            console.print("  [yellow]This field is required.[/yellow]")
            continue
        if validate_package_name(package_name):
            break
        console.print(
            "  [yellow]Invalid name. Use letters, numbers, and hyphens"
            " (e.g., my-package).[/yellow]"
        )

    package_underscore = to_underscore(package_name)
    package_title = package_name.replace("-", " ").title()
    description = ask_required("Package description")
    author_name = ask_required("Author name")
    author_email = ask_required("Author email")
    github_username = ask_required("GitHub username or organization")
    include_docs = Confirm.ask(
        "[bold]Include Starlight documentation site?[/bold]", default=True
    )

    current_year = str(datetime.now().year)

    print_header("Configuration summary")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("Package name", package_name)
    table.add_row("Python import", package_underscore)
    table.add_row("Description", description)
    table.add_row("Author", f"{author_name} <{author_email}>")
    table.add_row("GitHub", f"{github_username}/{package_name}")
    table.add_row("Documentation", "Yes (Starlight)" if include_docs else "No")
    console.print(table)
    console.print()

    if not Confirm.ask("Proceed with setup?", default=True):
        console.print("\n[yellow]Setup cancelled.[/yellow]")
        _uninstall_rich()
        return 1

    print_header("Configuring project")

    src_old = SCRIPT_DIR / "src" / "package_name"
    src_new = SCRIPT_DIR / "src" / package_underscore
    if src_old.exists():
        print_step(f"Renaming src/package_name/ to src/{package_underscore}/")
        shutil.move(str(src_old), str(src_new))
        print_success("Package directory renamed")

    replacements = {
        "opencitations/python-package-template": f"{github_username}/{package_name}",
        "python-package-template": package_name,
        "package-name": package_name,
        "package_name": package_underscore,
        "Package Name": package_title,
        "Python Package Template": package_title,
        "Package description": description,
        "A template for creating Python packages with UV, pytest, and Starlight documentation": description,
        "Author Name": author_name,
        "author@example.com": author_email,
        "opencitations": github_username,
        "[year]": current_year,
        "[author]": author_name,
    }

    files_to_update = [
        SCRIPT_DIR / "pyproject.toml",
        SCRIPT_DIR / "LICENSE.md",
        SCRIPT_DIR / "REUSE.toml",
        SCRIPT_DIR / "src" / package_underscore / "__init__.py",
        SCRIPT_DIR / "tests" / "__init__.py",
        SCRIPT_DIR / "tests" / "test_example.py",
        SCRIPT_DIR / ".github" / "workflows" / "tests.yml",
        SCRIPT_DIR / ".github" / "workflows" / "release.yml",
        SCRIPT_DIR / ".github" / "workflows" / "deploy-docs.yml",
        SCRIPT_DIR / ".github" / "workflows" / "reuse.yml",
    ]

    for filepath in files_to_update:
        if filepath.exists():
            print_step(f"Updating {filepath.relative_to(SCRIPT_DIR)}")
            replace_in_file(filepath, replacements)
            print_success(f"{filepath.name} updated")

    readme_template = SCRIPT_DIR / "README_TEMPLATE.md"
    readme_path = SCRIPT_DIR / "README.md"
    if readme_template.exists():
        print_step("Generating README.md from template...")
        content = readme_template.read_text()
        for old, new in replacements.items():
            content = content.replace(old, new)
        readme_path.write_text(content)
        print_success("README.md generated")

    docs_dir = SCRIPT_DIR / "docs"
    if include_docs:
        if docs_dir.exists():
            print_step("Updating documentation files...")
            docs_files = [
                docs_dir / "astro.config.mjs",
                docs_dir / "src" / "content.config.ts",
                docs_dir / "src" / "content" / "docs" / "index.mdx",
                docs_dir / "src" / "content" / "docs" / "getting_started.md",
            ]
            for filepath in docs_files:
                if filepath.exists():
                    replace_in_file(filepath, replacements)
            print_success("Documentation files updated")
    else:
        if docs_dir.exists():
            print_step("Removing documentation directory...")
            shutil.rmtree(docs_dir)
            print_success("docs/ removed")

        deploy_docs_workflow = SCRIPT_DIR / ".github" / "workflows" / "deploy-docs.yml"
        if deploy_docs_workflow.exists():
            print_step("Removing documentation workflow...")
            deploy_docs_workflow.unlink()
            print_success("deploy-docs.yml removed")

        reuse_toml = SCRIPT_DIR / "REUSE.toml"
        if reuse_toml.exists():
            print_step("Removing docs entries from REUSE.toml...")
            content = reuse_toml.read_text()
            content = re.sub(r'    "docs/[^\n]+\n', "", content)
            reuse_toml.write_text(content)
            print_success("REUSE.toml updated")

        if readme_path.exists():
            print_step("Updating README.md (removing docs section)...")
            content = readme_path.read_text()
            content = re.sub(
                r"\n## Documentation\n.*?(?=\n## |\Z)",
                "",
                content,
                flags=re.DOTALL,
            )
            content = re.sub(
                r"\n### Building documentation locally\n.*?(?=\n## |\n### |\Z)",
                "",
                content,
                flags=re.DOTALL,
            )
            readme_path.write_text(content)
            print_success("README.md updated")

    print_step("Running uv sync --all-extras --dev")
    success, output = run_command(
        ["uv", "sync", "--all-extras", "--dev"],
        cwd=SCRIPT_DIR,
    )
    if success:
        print_success("Dependencies installed")
    else:
        print_error("uv sync failed. Run it manually after setup.")
        console.print(output)

    print_step("Removing setup files")
    setup_files = [
        SCRIPT_DIR / "setup.py",
        SCRIPT_DIR / "README_TEMPLATE.md",
    ]
    for filepath in setup_files:
        if filepath.exists():
            filepath.unlink()

    images_dir = SCRIPT_DIR / ".github" / "images"
    if images_dir.exists():
        shutil.rmtree(images_dir)

    reuse_toml = SCRIPT_DIR / "REUSE.toml"
    if reuse_toml.exists():
        content = reuse_toml.read_text()
        content = re.sub(r'    "README_TEMPLATE\.md",\n', "", content)
        content = re.sub(r'    "\.github/images/\*\*",\n', "", content)
        reuse_toml.write_text(content)

    print_success("Setup files removed")

    _uninstall_rich()

    print_header("Setup complete")
    console.print("Your project is ready. Next steps:\n")
    console.print("[bold]1. Configure GitHub repository:[/bold]")
    console.print("   - Create PyPI token: https://pypi.org/manage/account/token/")
    console.print(
        f"   - Add as secret: https://github.com/{github_username}/{package_name}"
        "/settings/secrets/actions/new"
    )
    console.print("     Name: PYPI_TOKEN")
    if include_docs:
        console.print(
            f"   - Enable GitHub Pages: https://github.com/{github_username}"
            f"/{package_name}/settings/pages"
        )
        console.print("     Source: GitHub Actions")
    console.print()
    console.print("[bold]2. Commit and push:[/bold]")
    console.print('   git add .')
    console.print('   git commit -m "feat: initial project setup"')
    console.print("   git push")
    if include_docs:
        console.print()
        console.print(
            "   [yellow]Warning: if GitHub Pages is not configured with"
            " 'GitHub Actions' as source, the documentation deployment"
            " will fail.[/yellow]"
        )
    console.print()
    console.print("[bold]3. Start developing:[/bold]")
    console.print(f"   - Edit src/{package_underscore}/__init__.py")
    console.print("   - Add tests in tests/")
    if include_docs:
        console.print("   - Update documentation in docs/src/content/docs/")
    console.print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
