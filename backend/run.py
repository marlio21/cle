from state_engine.state_engine import StateEngine


def print_list(title: str, values: list[str]) -> None:
    print(f"\n{title}:")

    if not values:
        print("- keine")
        return

    for value in values:
        print(f"- {value}")


def main() -> None:
    engine = StateEngine()
    state = engine.analyze(".")

    print("\n===== PROJECT STATE =====")
    print(f"Projekt:    {state.project_name}")
    print(f"Existiert:  {state.exists}")
    print(f"Sprache:    {state.language}")
    print(f"Framework:  {state.framework}")
    print(f"Dateien:    {state.file_count}")

    print_list("Module", state.modules)
    print_list("Verzeichnisse", state.directories)
    print_list("Testdateien", state.test_files)


if __name__ == "__main__":
    main()