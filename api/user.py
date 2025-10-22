from flask import Blueprint, jsonify, request
from scripts.models.user import User
from scripts.models.session import Session
from scripts.models.activity import Activity
from app import db
from scripts.user_helpers import get_user, is_bot
from datetime import datetime, time
from scripts.user_helpers import get_device_type, format_referer
import math
from scripts.validate_admin import validate_admin_key
import time as time_module

user_bp = Blueprint("user", __name__)


@user_bp.route("/user/<user_id>", methods=["GET"])
@validate_admin_key
def get_user_totals_by_id(user_id):
    user_sessions: list[Session] = Session.query.filter(
        Session.user_id == user_id
    ).all()

    user_session_results = {}
    for session in user_sessions:
        user_session_results[session.id] = {
            "id": session.id,
            "device": get_device_type(session.user_agent),
            "start_time": session.start_time,
            "end_time": session.end_time,
            "pages_visited": len(session.activities),
            "videos_clicked": len(session.clicked_videos),
            "venues_viewed": session.num_venues_viewded,
            "bands_viewed": session.num_bands_viewed,
            "user_agent": session.user_agent,
            "referer": session.referer,
        }

    return jsonify({"sessions": user_session_results})


@user_bp.route("/session/<session_id>")
@validate_admin_key
def get_sesssion_details(session_id):
    activities: list[Activity] = Activity.query.filter(
        Activity.session_id == session_id
    ).all()

    results = {}
    for activity in activities:
        results[activity.id] = {
            "id": activity.id,
            "page": activity.page,
            "user_agent": activity.user_agent,
            "ip_address": activity.ip,
            "referer": activity.referer,
            "created_at": activity.created_at,
        }

    return jsonify({"activities": results})


@user_bp.route("/users", methods=["GET"])
@validate_admin_key
def get_user_totals():
    start_time = time_module.time()
    print("Getting user totals... Time: ", start_time)
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    to_date = datetime.combine(
        datetime.strptime(to_date, "%Y-%m-%d"), time(hour=23, minute=59, second=59)
    )
    include_admins = request.args.get("include_admins", "false")
    min_duration_seconds = request.args.get("min_duration_seconds")
    min_duration_seconds = int(min_duration_seconds)

    all_sessions: list[Session] = Session.query.filter(
        Session.start_time >= from_date, Session.start_time <= to_date
    ).all()

    print(
        f"Processing {len(all_sessions)} sessions... Time elapsed (seconds): ",
        time_module.time() - start_time,
    )

    user_results = {}
    total_new_sessions = 0
    total_returning_sessions = 0
    for session in all_sessions:
        # print(
        #     f"Processing session {session.id} for user {session.user_id}... Time elapsed (seconds): ",
        #     time_module.time() - start_time,
        # )
        user_id = session.user_id
        print("About to do if statement: ", time_module.time() - start_time)
        if (
            user_id not in user_results
            and (include_admins == "true" or not session.user.is_admin)
            and (
                (session.end_time - session.start_time).total_seconds()
                >= min_duration_seconds
            )
        ):
            print("Inside if statement: ", time_module.time() - start_time)
            user_results[user_id] = {
                "user_id": user_id,
                "duration": round(
                    (session.end_time - session.start_time).total_seconds() / 60, 2
                ),
                "device": get_device_type(session.user_agent),
                "referer": format_referer(session.referer),
                "videos_clicked": len(session.clicked_videos),
                "events_viewed": len(session.viewed_events),
                "type": (
                    "new" if session.user.sessions[0].id == session.id else "returning"
                ),
                "pages_visited": len(session.activities),
                "venues_viewed": session.num_venues_viewded,
                "bands_viewed": session.num_bands_viewed,
                "start_time": session.start_time,
            }
            if session.user.sessions[0].id == session.id:
                total_new_sessions += 1
            else:
                total_returning_sessions += 1
            print("Finish if statement: ", time_module.time() - start_time)
        elif (include_admins == "true" or not session.user.is_admin) and (
            (session.end_time - session.start_time).total_seconds()
            > min_duration_seconds
        ):
            print("Inside elif statement: ", time_module.time() - start_time)
            user_results[user_id]["duration"] += round(
                (session.end_time - session.start_time).total_seconds() / 60, 2
            )
            user_results[user_id]["videos_clicked"] += len(session.clicked_videos)
            user_results[user_id]["events_viewed"] += len(session.viewed_events)
            user_results[user_id]["pages_visited"] += len(session.activities)
            user_results[user_id]["venues_viewed"] += session.num_venues_viewded
            user_results[user_id]["bands_viewed"] += session.num_bands_viewed
            if session.user.sessions[0].id == session.id:
                user_results[user_id]["type"] = "new"
                total_new_sessions += 1
            else:
                total_returning_sessions += 1
            print("Finish elif statement: ", time_module.time() - start_time)

    print(
        "Finished processing users. Time elapsed (seconds): ",
        time_module.time() - start_time,
    )

    # Get totals
    totals = {
        "total_users": len(user_results),
        "total_new_users": sum(
            1 for user in user_results.values() if user["type"] == "new"
        ),
        "total_returning_users": sum(
            1 for user in user_results.values() if user["type"] == "returning"
        ),
        "total_sessions": total_new_sessions + total_returning_sessions,
        "total_new_sessions": total_new_sessions,
        "total_returning_sessions": total_returning_sessions,
        "total_mobile_users": sum(
            1 for user in user_results.values() if user["device"] == "mobile"
        ),
        "total_tablet_users": sum(
            1 for user in user_results.values() if user["device"] == "tablet"
        ),
        "total_computer_users": sum(
            1 for user in user_results.values() if user["device"] == "computer"
        ),
        "total_facebook_referers": sum(
            1 for user in user_results.values() if user["referer"] == "facebook"
        ),
        "total_reddit_referers": sum(
            1 for user in user_results.values() if user["referer"] == "reddit"
        ),
        "total_google_referers": sum(
            1 for user in user_results.values() if user["referer"] == "google"
        ),
        "total_patch_referers": sum(
            1 for user in user_results.values() if user["referer"] == "patch"
        ),
        "total_unknown_referers": sum(
            1 for user in user_results.values() if user["referer"] == "unknown"
        ),
        "total_videos_clicked": sum(
            user["videos_clicked"] for user in user_results.values()
        ),
        "total_events_viewed": sum(
            user["events_viewed"] for user in user_results.values()
        ),
        "total_pages_visited": sum(
            user["pages_visited"] for user in user_results.values()
        ),
        "total_duration": sum(user["duration"] for user in user_results.values()),
        "total_venues_viewed": sum(
            user["venues_viewed"] for user in user_results.values()
        ),
        "total_bands_viewed": sum(
            user["bands_viewed"] for user in user_results.values()
        ),
    }

    print(
        "Finished processing totals. Time elapsed (seconds): ",
        time_module.time() - start_time,
    )

    return jsonify({"users": user_results, "totals": totals}), 200


@user_bp.route("/video-clicked", methods=["POST"])
def add_video_click():
    # Check if the request came from a bot
    user_agent = request.json["user_agent"]
    user_is_bot = is_bot(user_agent)
    if not user_is_bot:
        # Get parameters
        user_id = request.json["user_id"]
        event_id = request.json["event_id"]

        user: User = get_user(user_id, db)
        user.add_video_click(event_id)
        db.session.commit()

    return jsonify({"status": "success"}), 200


@user_bp.route("/track-user-exit/<user_id>", methods=["POST"])
def track_user_exit(user_id):
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        return jsonify({"status": "No user found."}), 200
    else:
        user.track_exit()
        db.session.commit()
        return jsonify({"status": "Exit Tracked"}), 200


@user_bp.route("/activity", methods=["POST"])
def add_activity():
    user_agent = request.json["user_agent"]
    page = request.json["page"]
    ip = request.json["ip"]
    referer = request.json["referer"]
    user_is_bot = is_bot(
        user_agent,
        is_query=False,
        page=page,
        ip=ip,
        referer=referer,
        track_activity=True,
    )

    if not user_is_bot:
        user_id = request.json["user_id"]
        user: User = get_user(user_id, db)
        user.add_activity(page, user_agent, ip, referer)
        db.session.commit()

    return jsonify({"status": "success"}), 200
