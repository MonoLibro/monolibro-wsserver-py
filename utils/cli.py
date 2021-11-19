def yn_question(question: str) -> bool:
    answer = None
    while answer != "y" and answer != "n":
        answer = input(f"{question} (y/n): ").lower()
    return answer == "y"
