import logging

from time import sleep
from soco_cli.api import run_command, get_soco_object
from soco_cli.utils import error_and_exit


def track_follow(speaker, use_local_speaker_list=False, break_on_pause=True):
    """Print out the 'track' details each time the track changes.

    Args:
        speaker (SoCo): The speaker to follow.
        break_on_pause (bool, optional): Whether to return control if the
            speaker enters the paused or stopped playback states.
    """

    first = True
    while True:
        # If stopped, wait for the speaker to start playback
        if speaker.get_current_transport_info()["current_transport_state"] in [
            "STOPPED",
            "PAUSED_PLAYBACK",
        ]:
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
            output = output.replace("Playback state is 'PLAYING':\n", "")
            output = output.replace("Playback state is 'TRANSITIONING':\n", "")
            if not first:
                output = output.split("\n", 1)[1]
            else:
                first = False
            print(output)
        else:
            print(error_msg)

        # Wait until the track changes
        logging.info("Waiting for end of track")
        run_command(
            speaker, "wait_end_track", use_local_speaker_list=use_local_speaker_list
        )

        # Allow speaker state to stabilise
        logging.info("Waiting 3s for playback to stabilise")
        sleep(3)
