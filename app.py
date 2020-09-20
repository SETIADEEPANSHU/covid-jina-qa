__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os

import click
from jina.flow import Flow


def config():
    os.environ["JINA_DATA_FILE"] = os.environ.get(
        "JINA_DATA_FILE", "data/covd_final_qa.csv"
    )
    os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "workspace")

    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45678))


def print_topk(resp, sentence):
    for d in resp.search.docs:
        print(f"Jina Covid Bot🔮, Lets Burst your myths and present you real facts (No) {sentence}")
        for idx, match in enumerate(d.matches):

            score = match.score.value
            if score < 0.0:
                continue
            # answer = match.meta_info.decode()
            question = match.meta_info.decode()
            answer = match.text.strip()
            print(f'> {idx:>2d}({score:.2f}). {answer.upper()} Query , "{question}"')


def index(num_docs):
    f = Flow().load_config("flow-index.yml")

    with f:
        f.index_lines(
            filepath=os.environ["JINA_DATA_FILE"],
            batch_size=8,
            size=num_docs,
        )


def query(top_k):
    f = Flow().load_config("flow-query.yml")
    with f:
        while True:
            text = input("please type your covid related query: ")
            if not text:
                break

            def ppr(x):
                print_topk(x, text)
            f.search_lines(lines=[text, ], output_fn=ppr, top_k=top_k)


def query_restful():
    f = Flow().load_config("flow-query.yml")
    f.use_rest_gateway()
    with f:
        f.block()


def dryrun():
    f = Flow().load_config("flow-index.yml")
    with f:
        f.dry_run()


@click.command()
@click.option(
    "--task",
    "-t",
    type=click.Choice(
        ["index", "query", "query_restful", "dryrun"], case_sensitive=False
    ),
)
@click.option("--num_docs", "-n", default=50)
@click.option("--top_k", "-k", default=5)
def main(task, num_docs, top_k):
    config()
    if task == "index":
        index(num_docs)
    if task == "query":
        query(top_k)
    if task == "query_restful":
        query_restful()
    if task == "dryrun":
        dryrun()


if __name__ == "__main__":
    main()
