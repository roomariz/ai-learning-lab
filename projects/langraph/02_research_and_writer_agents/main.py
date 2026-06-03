from research_and_writer_agents import article_graph


def main() -> None:
    topic = input("Enter topic: ")

    print("\nRunning LangGraph article workflow...")

    result = article_graph.invoke({
        "topic": topic,
        "plan": "",
        "article": "",
        "edited_article": "",
    })

    print("\n--- FINAL EDITED ARTICLE ---\n")
    print(result["edited_article"])


if __name__ == "__main__":
    main()