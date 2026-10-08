from skills.trading.freqtrade import FreqtradeAdapter


def test_dry_run_execution():
    adapter = FreqtradeAdapter(dry_run=True)

    result = adapter.execute(
        "buy",
        {"symbol": "BTC/USDT"},
    )

    assert result.success is True
    assert result.status == "DRY_RUN"
    assert result.data["operation"] == "buy"


def test_live_execution_is_blocked():
    adapter = FreqtradeAdapter(dry_run=False)

    result = adapter.execute(
        "buy",
        {"symbol": "BTC/USDT"},
    )

    assert result.success is False
    assert result.status == "BLOCKED"


def test_adapter_does_not_modify_parameters():
    adapter = FreqtradeAdapter(dry_run=True)

    parameters = {
        "symbol": "BTC/USDT",
        "amount": 1.0,
    }

    result = adapter.execute("buy", parameters)

    assert result.data["parameters"] == parameters
