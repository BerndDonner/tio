#!/usr/bin/env python3

import time

from _test_runner import TioSession

def test_expect_match():
    script = """
tio.alwaysecho = false
tio.write("READY")

local data = tio.expect("OK", 1000)
if data then
    print("EXPECT_OK:" .. data)
else
    print("EXPECT_TIMEOUT")
end
tio.alwaysecho = true
"""
    with TioSession(script, ready=b"READY") as session:
        session.write_serial(b"OK")
        session.wait_stdout(b"EXPECT_OK:OK")


def test_expect_capture():
    script = """
tio.alwaysecho = false
tio.write("READY")
local value, data = tio.expect("VALUE:(%d+)", 1000)
if value then
    print("CAPTURE:" .. value .. ":" .. data)
else
    print("CAPTURE_TIMEOUT")
end
tio.alwaysecho = true
"""
    with TioSession(script, ready=b"READY") as session:
        session.write_serial(b"VALUE:123")
        session.wait_stdout(b"CAPTURE:123:VALUE:123")


def test_expect_timeout_returns_received_data():
    script = """
tio.alwaysecho = false
tio.write("READY")
local data, received = tio.expect("NEVER", 1000)
if data == nil then
    print("TIMEOUT:" .. received)
else
    print("UNEXPECTED")
end

tio.alwaysecho = true
"""
    with TioSession(script, ready=b"READY") as session:
        session.write_serial(b"abc")
        session.wait_stdout(b"TIMEOUT:abc")


def test_expect_match_across_chunks():
    script = """
tio.alwaysecho = false
tio.write("READY")
local data = tio.expect("OK", 1000)
if data then
    print("CROSS:" .. data)
else
    print("CROSS_TIMEOUT")
end
tio.alwaysecho = true
"""
    with TioSession(script, ready=b"READY") as session:
        session.write_serial(b"O")
        time.sleep(0.05)
        session.write_serial(b"K")
        session.wait_stdout(b"CROSS:OK")


def test_expect_match_with_preceding_data():
    script = """
tio.alwaysecho = false
tio.write("READY")
local data = tio.expect(".*OK", 1000)
if data then
    print("PRECEDING:" .. data)
else
    print("PRECEDING_TIMEOUT")
end
tio.alwaysecho = true
"""
    with TioSession(script, ready=b"READY") as session:
        session.write_serial(b"abcOK")
        session.wait_stdout(b"PRECEDING:abcOK")


def test_expects_first_pattern():
    script = """
tio.alwaysecho = false
tio.write("READY")
local index, data = tio.expects({"ERROR", "OK"}, 1000)
if index then
    print(string.format("MATCH:%d:%s", index, data[index]))
else
    print("TIMEOUT")
end
tio.alwaysecho = true
"""
    with TioSession(script, ready=b"READY") as session:
        session.write_serial(b"ERROR")
        session.wait_stdout(b"MATCH:1:ERROR")


def test_expects_second_pattern_with_capture():
    script = """
tio.alwaysecho = false
tio.write("READY")
local index, value, data =
    tio.expects({"ERROR", "OK (%d+)"}, 1000)

if index then
    print(string.format("MATCH:%d:%s:%s", index, value[1], data))
else
    print("TIMEOUT")
end
tio.alwaysecho = true
"""
    with TioSession(script, ready=b"READY") as session:
        session.write_serial(b"OK 123")
        session.wait_stdout(b"MATCH:2:123:OK 123")


def test_expects_timeout_returns_received_data():
    script = """
tio.alwaysecho = false
tio.write("READY")
local index, value, data = tio.expects({"ERROR", "OK"}, 1000)
if index == nil then
    print("TIMEOUT:" .. data)
else
    print("UNEXPECTED")
end
tio.alwaysecho = true
"""
    with TioSession(script, ready=b"READY") as session:
        session.write_serial(b"hello")
        session.wait_stdout(b"TIMEOUT:hello")


def test_expects_match_across_chunks():
    script = """
tio.alwaysecho = false
tio.write("READY")
local index, value, data = tio.expects({"ERROR", "OK"}, 1000)
if index then
    print(string.format("CROSS:%d:%s", index, value[1]))
else
    print("CROSS_TIMEOUT")
end
tio.alwaysecho = true
"""
    with TioSession(script, ready=b"READY") as session:
        session.write_serial(b"O")
        time.sleep(0.05)
        session.write_serial(b"K")
        session.wait_stdout(b"CROSS:2:OK")


def test_expect_special_lua_pattern():
    script = """
tio.alwaysecho = false
tio.write("READY")
local data = tio.expect("VALUE:%s+(%d+)", 1000)
if data then
    print("PATTERN:" .. data)
else
    print("PATTERN_TIMEOUT")
end
tio.alwaysecho = true
"""
    with TioSession(script, ready=b"READY") as session:
        session.write_serial(b"VALUE:   42")
        session.wait_stdout(b"PATTERN:42")


def test_expect_multiple_calls_consume_previous_match():
    script = """
tio.alwaysecho = false
tio.write("READY")
local first, data_1st = tio.expect("ONE", 1000)
local second, data_2nd = tio.expect("TWO", 1000)

    print("DATA1ST:" .. data_1st .. ":DATA2ND" .. data_2nd)

if first and second then
    print("BOTH:" .. first .. ":" .. second)
else
    print("FAILED")
end
tio.alwaysecho = true
"""
    with TioSession(script, ready=b"READY") as session:
        session.write_serial(b"ONETWO")
        session.wait_stdout(b"BOTH:ONE:TWO")


def test_expects_multiple_patterns_selects_earliest_match():
    script = """
tio.alwaysecho = false
tio.write("READY")
local index, value, data = tio.expects({".*AAA", ".*BBB"}, 1000)
if index then
    print(string.format("EARLIEST:%d:%s", index, value[1]))
else
    print("TIMEOUT")
end
tio.alwaysecho = true
"""
    with TioSession(script, ready=b"READY") as session:
        session.write_serial(b"xxBBByyAA")
        session.wait_stdout(b"EARLIEST:2:xxBBB")


EXPECT_TESTS = [
    test_expect_match,
    test_expect_capture,
    test_expect_timeout_returns_received_data,
    test_expect_match_across_chunks,
    test_expect_match_with_preceding_data,
    test_expects_first_pattern,
    test_expects_second_pattern_with_capture,
    test_expects_timeout_returns_received_data,
    test_expects_match_across_chunks,
    test_expect_special_lua_pattern,
    test_expects_multiple_patterns_selects_earliest_match,
]
