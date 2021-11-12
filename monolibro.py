import asyncio
import monolibro
import click


@click.command()
@click.option("-h", "--host", default="127.0.0.1", type=str, help="Proxy host address.")
@click.option("-p", "--port", default=3200, type=int, help="Proxy port.")
def main(host, port):
    wss = monolibro.Proxy(host, port)

    asyncio.run(wss.start())


if __name__ == "__main__":
    main()
