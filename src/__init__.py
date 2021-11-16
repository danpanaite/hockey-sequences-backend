import json
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import cross_origin
from . import db


def to_json(df):
    return jsonify(json.loads(df.to_json(orient="records")))


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev", DATABASE="database.db")

    @app.route("/games")
    @cross_origin()
    def get_plays():
        return to_json(pd.read_sql_query("SELECT * from games", db.get_db()))

    @app.route("/sequences")
    @cross_origin()
    def get_sequences():
        game_date = request.args.get("game_date")
        query = f"SELECT * FROM play_sequences"

        if game_date is not None:
            query = f"{query} WHERE game_date='{game_date}'"

        print(query)

        return to_json(pd.read_sql_query(query, db.get_db()))

    @app.route("/sequences/<id>/plays")
    @cross_origin()
    def get_sequence_plays(id):
        sequence = pd.read_sql_query(
            f"SELECT * from play_sequences WHERE id = '{id}' LIMIT 1", db.get_db()
        ).iloc[0]

        return to_json(
            pd.read_sql_query(
                f"""
                    SELECT * from plays
                    WHERE team = '{sequence.team}'
                    AND game_date = '{sequence.game_date}'
                    AND seconds_elapsed >= '{sequence.start_time}' 
                    AND seconds_elapsed <= '{sequence.end_time}'""",
                db.get_db(),
            )
        )

    db.init_app(app)

    return app
