import logging
import re

from datetime import datetime, timezone
from time import sleep
from soco_cli.api import run_command


def track_follow(speaker, use_local_speaker_list=False, break_on_pause=True):
    """Print out the 'track' details each time the track changes.

    Args:
        speaker (SoCo): The speaker to follow.
        use_local_speaker_list (bool, optional): Use cached discovery.
        break_on_pause (bool, optional): Whether to return control if the
            speaker enters the paused or stopped playback states.

    This function operates as if 'outside' the main program logic, because
    it needs to output intermediate results as it executes. Hence, the
    'run_command()' API call is used.
    """

    def timestamp():
        local_tz = datetime.now(timezone.utc).astimezone().tzinfo
        return datetime.now(tz=local_tz).strftime("%d-%b-%Y %H:%M:%S %Z")

    print(flush=True)
    while True:
        # If stopped, wait for the speaker to start playback
        _, state, _ = run_command(
            speaker, "state", use_local_speaker_list=use_local_speaker_list
        )
        if state in [
            "STOPPED",
            "PAUSED_PLAYBACK",
        ]:
            print(
                " Playback is stopped or paused at: {}\n".format(timestamp()),
                flush=True,
            )
            if break_on_pause:
                logging.info("Playback is paused/stopped; returning")
                break
            logging.info("Playback is paused/stopped; waiting for start")
            run_command(
                speaker, "wait_start", use_local_speaker_list=use_local_speaker_list
            )
            logging.info("Speaker has started playback")

        # Print the track info
        exit_code, output, error_msg = run_command(
            speaker, "track", use_local_speaker_list=use_local_speaker_list
        )
        if exit_code == 0:
            # Restructure output
            output = output.split("\n ", 1)[1]
            output = " Time: " + timestamp() + "\n" + output
            output = re.sub("Playlist_position", "Playlist Position", output)
            # Remove some of the entries
            output = re.sub("Playback.*\\n", "", output)
            output = re.sub("   Position.*\\n", "", output)
            output = re.sub("   URI.*\\n", "", output)
            output = re.sub("   Uri.*\\n", "", output)
            print(output, flush=True)
        else:
            print(error_msg, flush=True)

        # Wait until the track changes
        logging.info("Waiting for end of track")
        run_command(
            speaker, "wait_end_track", use_local_speaker_list=use_local_speaker_list
        )

        # Allow speaker state to stabilise
        logging.info("Waiting 1s for playback to stabilise")
        sleep(1.0)
