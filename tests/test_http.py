import httpx
import pytest

from briefing.http import USER_AGENT, FixtureClient, HttpxClient, RecordingClient


def make_client(handler, sleeps, **kwargs):
    return HttpxClient(
        transport=httpx.MockTransport(handler),
        sleep=sleeps.append,
        clock=lambda: 0.0,
        min_interval=0,
        **kwargs,
    )


def test_sends_user_agent_and_params():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, text="ok")

    assert make_client(handler, []).get("https://example.com/x", {"a": "1"}) == "ok"
    assert seen[0].headers["user-agent"] == USER_AGENT
    assert seen[0].url.params["a"] == "1"


def test_retries_server_errors_twice_then_succeeds():
    attempts = []

    def handler(request):
        attempts.append(1)
        return httpx.Response(503 if len(attempts) < 3 else 200, text="done")

    sleeps = []
    assert make_client(handler, sleeps).get("https://example.com") == "done"
    assert len(attempts) == 3
    assert sleeps == [1, 2]


def test_gives_up_after_two_retries():
    attempts = []

    def handler(request):
        attempts.append(1)
        return httpx.Response(500)

    with pytest.raises(httpx.HTTPStatusError):
        make_client(handler, []).get("https://example.com")
    assert len(attempts) == 3


def test_does_not_retry_client_errors():
    attempts = []

    def handler(request):
        attempts.append(1)
        return httpx.Response(404)

    with pytest.raises(httpx.HTTPStatusError):
        make_client(handler, []).get("https://example.com")
    assert len(attempts) == 1


def test_waits_between_calls():
    now = [0.0]
    sleeps = []
    client = HttpxClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, text="ok")),
        sleep=sleeps.append,
        clock=lambda: now[0],
        min_interval=1.0,
    )
    client.get("https://example.com/1")
    now[0] = 0.25
    client.get("https://example.com/2")
    assert sleeps == [0.75]


def test_recording_client_saves_then_fixture_client_replays(tmp_path):
    class Inner:
        def get(self, url, params=None):
            return f"body of {url}"

    recorder = RecordingClient(Inner(), tmp_path / "out", "src", ".xml")
    recorder.get("a")
    recorder.get("b")
    assert (tmp_path / "out" / "src.xml").read_text(encoding="utf-8") == "body of a"
    assert (tmp_path / "out" / "src-2.xml").read_text(encoding="utf-8") == "body of b"

    replay = FixtureClient(tmp_path / "out", "src", ".xml")
    assert [replay.get("x"), replay.get("y")] == ["body of a", "body of b"]
