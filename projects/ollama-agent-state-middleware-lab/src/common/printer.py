def print_section(title: str) -> None:
    line = "=" * len(title)
    print(f"\n{title}\n{line}")


def print_turn(role: str, content: str) -> None:
    print(f"\n{role.upper()}:")
    print(content)