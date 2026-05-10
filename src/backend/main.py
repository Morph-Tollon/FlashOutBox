from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pyosc import Peer, OSCMessage, OSCString, OSCModes, OSCFraming
from return_models import VersionModel, PingResponseModel
import pathlib
import tomllib
import os
import logging
from datetime import datetime
from validators import (
    PingValidator,
    ActiveCueValidator,
    ActiveCompletionValidator,
    ActiveCueNumberValidator,
)
from validators import ActiveQueue, ActiveQueueItem
import time
logger = logging.getLogger("uvicorn.error")




def initialize_eos_peer():
    ip = str(os.getenv("DESK_IP"))
    port = int(os.getenv("DESK_PORT", "3032"))
    if not ip:
        raise ValueError("DESK_IP environment variable is not set")
    try:
        peer = Peer(address=ip, port=port, mode=OSCModes.TCP, framing=OSCFraming.OSC11)
        peer.start_listening()

        return peer
    except Exception as e:
        logger.error(f"Error initializing OSC peer: {e}")
        raise e


def get_version():
    with open(pathlib.Path(__file__).parent / "pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    return pyproject["project"]["version"]


def active_handler(message) -> None:
    print(message)
    if isinstance(message, ActiveCueNumberValidator):
        app.state.eos_active.put(
            ActiveQueueItem(
                number=message.number, list=message.list, completion=message.completion
            )
        )
    else:
        app.state.eos_active.completion(message.completion)


def register_handlers():
    app.state.eos_peer.register_handler(
        address="/eos/out/active/cue/*/*",
        func=active_handler,
        validator=ActiveCueNumberValidator,
    )
    app.state.eos_peer.register_handler(
        address="/eos/out/active/cue",
        func=active_handler,
        validator=ActiveCompletionValidator,
    )
    # Sends reset command, forcing Eos to return the current acttive cue information.
    app.state.eos_peer.send_message(
        message=OSCMessage(
            address='/eos/reset',
            args=()))



@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.eos_peer = initialize_eos_peer()
    app.state.eos_active = ActiveQueue()
    try:
        response = app.state.eos_peer.call(
            message=OSCMessage(
                address="/eos/ping", args=(OSCString(value="Ping From FlashOutBox"),)
            ),
            return_address="/eos/out/ping",
            validator=PingValidator,
        )
        if response:
            register_handlers()
            if (
                not isinstance(response, list)
                and response.message.message == "Ping From FlashOutBox"
            ):
                logger.info(
                    f"Received ping response from EOS during startup: {response.message.message}"
                )

            else:
                raise ValueError(
                    "Unexpected response from EOS during startup ping. Expected a message with 'Ping From FlashOutBox'."
                )
        else:
            raise ValueError("No response received from EOS during startup ping.")

    except Exception as e:
        logger.error(f"Error during OSC peer initialization: {e}")
        raise e

    yield
    app.state.eos_peer.stop_listening()


app = FastAPI(
    title="FlashOutBox Backend API",
    description="A simple API to remote control basic functions of a lighting console",
    version=get_version(),
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Local development server"}
    ],
    contact={"name": "Morph Tollon", "email": "code@morphtollon.co.uk"},
    debug=True,
    lifespan=lifespan,
)


@app.get("/version", response_model=VersionModel)
def version():
    return VersionModel(app_version=app.version)


@app.get(
    "/ping",
    description="Returns a round trip time from the backend to eos and then back.",
    response_model=PingResponseModel,
)
def ping():
    start_time = datetime.now()
    try:
        response = app.state.eos_peer.call(
            message=OSCMessage(
                address="/eos/ping",
                args=(OSCString(value=str(start_time.timestamp())),),
            ),
            return_address="/eos/out/ping",
            validator=PingValidator,
        )
        if response:
            if not isinstance(response, list) and isinstance(
                response.message, PingValidator
            ):
                end_time = datetime.now()
                round_trip_time = (
                    end_time - start_time
                ).total_seconds() * 1000  # Convert to milliseconds
                logger.info(
                    f"Received ping response from EOS: {response.message.message}, Round Trip Time: {round_trip_time:.2f} ms"
                )
                return PingResponseModel(
                    round_trip_time_ms=round_trip_time, osc_latency_ms=response.latency
                )

    except Exception as e:
        logger.error(f"Error during ping: {e}")
        raise HTTPException(status_code=500, detail="Error during ping")


@app.post(
    "/go",
    description="Fires the next cue, and returns information related to the next cue.",
)
def go():
    if app.state.eos_active.current.complete:
        try:
            app.state.eos_peer.send_message(
                message=OSCMessage(
                    address="/eos/cues/fire",
                    args=(),
                )
            )
        
            time.sleep(0.1)  # Small delay to allow EOS to process the command and update the active cue
            active = get_active_cue()
            return active

        except Exception as e:
            logger.error(f"Error sending go command: {e}")
            raise HTTPException(status_code=500, detail="Error sending go command")
    else:
        raise HTTPException(status_code=400, detail="Current cue is not complete yet.")

@app.get("/cue", description="Returns information about the currently active cue.")
def get_active_cue():
    active_cue = app.state.eos_active.current
    if not active_cue:
        raise HTTPException(status_code=404, detail="No active cue found")
    try:
        response = app.state.eos_peer.call(
            message=OSCMessage(
                address=f'/eos/get/cue/{active_cue.list}/{active_cue.number}',
                args=(),
            ),
            return_address='/eos/out/get/cue/*/*/*/list/*/*',
            validator=ActiveCueValidator,
        )
        print(response.message.cue_note)
        return {
            "number": active_cue.number,
            "list": active_cue.list,
            "completion": active_cue.completion,
            "complete": active_cue.complete,
            "note": response.message.cue_note,
        }
    except Exception as e:
        logger.error(f"Error sending get active cue command: {e}")
        raise HTTPException(
            status_code=500, detail="Error sending get active cue command"
        )
