import pandas as pd
import run_pipeline as pipeline


class DummyLogger:
    def info(self, message):
        pass

    def exception(self, message):
        pass


def test_run_pipeline(monkeypatch):
    sample = {
        "customers": pd.DataFrame({"customer_id": [1]})
    }

    monkeypatch.setattr(
        pipeline, "setup_logger", lambda: DummyLogger()
    )
    monkeypatch.setattr(
        pipeline, "load_all_data", lambda path: sample
    )
    monkeypatch.setattr(
        pipeline, "validate_all_tables", lambda data: True
    )
    monkeypatch.setattr(
        pipeline, "clean_data", lambda data: data
    )

    saved = {}
    monkeypatch.setattr(
        pipeline,
        "save_cleaned_data",
        lambda data, output_dir: saved.update({
            "data": data,
            "output_dir": output_dir,
        }),
    )

    result = pipeline.run_pipeline()

    assert result is sample
    assert saved["data"] is sample
    assert saved["output_dir"] == "data/cleaned"