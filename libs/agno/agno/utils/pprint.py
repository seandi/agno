import json
from typing import AsyncIterable, Iterable, Union, get_args

from pydantic import BaseModel

from agno.run.response import RunResponse, RunResponseEvent
from agno.run.team import TeamRunResponse, TeamRunResponseEvent
from agno.run.v2.workflow import WorkflowRunResponse, WorkflowRunResponseEvent
from agno.utils.log import logger
from agno.utils.timer import Timer


def pprint_run_response(
    run_response: Union[
        RunResponse,
        Iterable[RunResponseEvent],
        TeamRunResponse,
        Iterable[TeamRunResponseEvent],
        WorkflowRunResponse,
        Iterable[WorkflowRunResponseEvent],
    ],
    markdown: bool = False,
    show_time: bool = False,
) -> None:
    from rich.box import ROUNDED
    from rich.json import JSON
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.status import Status
    from rich.table import Table

    from agno.cli.console import console

    # If run_response is a single RunResponse, wrap it in a list to make it iterable
    if (
        isinstance(run_response, RunResponse)
        or isinstance(run_response, TeamRunResponse)
        or isinstance(run_response, WorkflowRunResponse)
    ):
        single_response_content: Union[str, JSON, Markdown] = ""
        if isinstance(run_response.content, str):
            single_response_content = (
                Markdown(run_response.content) if markdown else run_response.get_content_as_string(indent=4)
            )
        elif isinstance(run_response.content, BaseModel):
            try:
                single_response_content = JSON(run_response.content.model_dump_json(exclude_none=True), indent=2)
            except Exception as e:
                logger.warning(f"Failed to convert response to Markdown: {e}")
        else:
            try:
                single_response_content = JSON(json.dumps(run_response.content), indent=4)
            except Exception as e:
                logger.warning(f"Failed to convert response to string: {e}")

        table = Table(box=ROUNDED, border_style="blue", show_header=False)
        table.add_row(single_response_content)
        console.print(table)
    else:
        streaming_response_content: str = ""
        with Live(console=console) as live_log:
            status = Status("Working...", spinner="dots")
            live_log.update(status)
            response_timer = Timer()
            response_timer.start()
            for resp in run_response:
                if (
                    (
                        isinstance(resp, tuple(get_args(RunResponseEvent)))
                        or isinstance(resp, tuple(get_args(TeamRunResponseEvent)))
                        or isinstance(resp, tuple(get_args(WorkflowRunResponseEvent)))
                    )
                    and hasattr(resp, "content")
                    and resp.content is not None
                ):
                    if isinstance(resp.content, BaseModel):
                        try:
                            JSON(resp.content.model_dump_json(exclude_none=True), indent=2)  # type: ignore
                        except Exception as e:
                            logger.warning(f"Failed to convert response to Markdown: {e}")
                    else:
                        if isinstance(streaming_response_content, JSON):
                            streaming_response_content = streaming_response_content.text + "\n"  # type: ignore
                        streaming_response_content += resp.content  # type: ignore

                formatted_response = Markdown(streaming_response_content) if markdown else streaming_response_content  # type: ignore
                table = Table(box=ROUNDED, border_style="blue", show_header=False)
                if show_time:
                    table.add_row(f"Response\n({response_timer.elapsed:.1f}s)", formatted_response)  # type: ignore
                else:
                    table.add_row(formatted_response)  # type: ignore
                live_log.update(table)
            response_timer.stop()


async def apprint_run_response(
    run_response: Union[
        RunResponse,
        AsyncIterable[RunResponse],
        TeamRunResponse,
        AsyncIterable[TeamRunResponse],
        WorkflowRunResponse,
        AsyncIterable[WorkflowRunResponseEvent],
    ],
    markdown: bool = False,
    show_time: bool = False,
) -> None:
    from rich.box import ROUNDED
    from rich.json import JSON
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.status import Status
    from rich.table import Table

    from agno.cli.console import console

    # If run_response is a single RunResponse, wrap it in a list to make it iterable
    if (
        isinstance(run_response, RunResponse)
        or isinstance(run_response, TeamRunResponse)
        or isinstance(run_response, WorkflowRunResponse)
    ):
        single_response_content: Union[str, JSON, Markdown] = ""
        if isinstance(run_response.content, str):
            single_response_content = (
                Markdown(run_response.content) if markdown else run_response.get_content_as_string(indent=4)
            )
        elif isinstance(run_response.content, BaseModel):
            try:
                single_response_content = JSON(run_response.content.model_dump_json(exclude_none=True), indent=2)
            except Exception as e:
                logger.warning(f"Failed to convert response to Markdown: {e}")
        else:
            try:
                single_response_content = JSON(json.dumps(run_response.content), indent=4)
            except Exception as e:
                logger.warning(f"Failed to convert response to string: {e}")

        table = Table(box=ROUNDED, border_style="blue", show_header=False)
        table.add_row(single_response_content)
        console.print(table)
    else:
        streaming_response_content: str = ""
        with Live(console=console) as live_log:
            status = Status("Working...", spinner="dots")
            live_log.update(status)
            response_timer = Timer()
            response_timer.start()

            async for resp in run_response:
                if (
                    (
                        isinstance(resp, tuple(get_args(RunResponseEvent)))
                        or isinstance(resp, tuple(get_args(TeamRunResponseEvent)))
                        or isinstance(resp, tuple(get_args(WorkflowRunResponseEvent)))
                    )
                    and hasattr(resp, "content")
                    and resp.content is not None
                ):
                    if isinstance(resp.content, BaseModel):
                        try:
                            streaming_response_content = JSON(resp.content.model_dump_json(exclude_none=True), indent=2)  # type: ignore
                        except Exception as e:
                            logger.warning(f"Failed to convert response to Markdown: {e}")
                    else:
                        streaming_response_content += resp.content  # type: ignore

                formatted_response = Markdown(streaming_response_content) if markdown else streaming_response_content  # type: ignore
                table = Table(box=ROUNDED, border_style="blue", show_header=False)
                if show_time:
                    table.add_row(f"Response\n({response_timer.elapsed:.1f}s)", formatted_response)  # type: ignore
                else:
                    table.add_row(formatted_response)  # type: ignore
                live_log.update(table)
            response_timer.stop()
