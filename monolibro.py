import asyncio
import monolibro
import click
import utils


@click.command()
@click.option("-h", "--host", default="127.0.0.1", type=str, help="Proxy host address.")
@click.option("-p", "--port", default=3200, type=int, help="Proxy port.")
def main(host, port):
    logger = utils.Logger(write_to_file=False)
    wss = monolibro.Proxy(host, port, logger)

    try:
        logger.info("Press ^C to Abort")
        asyncio.run(wss.start())
    except KeyboardInterrupt:
        logger.info("Aborted!")
        logger.close()


if __name__ == "__main__":
    main()
