import time
import random
import datetime

import pytest
import pytz

from tempora import schedule


@pytest.fixture
def naive_times(monkeypatch):
	monkeypatch.setattr('irc.schedule.from_timestamp',
		datetime.datetime.fromtimestamp)
	monkeypatch.setattr('irc.schedule.now', datetime.datetime.now)


def test_delayed_command_order():
	"""
	delayed commands should be sorted by delay time
	"""
	null = lambda: None
	delays = [random.randint(0, 99) for x in range(5)]
	cmds = sorted([
		schedule.DelayedCommand.after(delay, null)
		for delay in delays
	])
	assert [c.delay.seconds for c in cmds] == sorted(delays)

def test_periodic_command_delay():
	"A PeriodicCommand must have a positive, non-zero delay."
	with pytest.raises(ValueError) as exc_info:
		schedule.PeriodicCommand.after(0, None)
	assert str(exc_info.value) == test_periodic_command_delay.__doc__

def test_periodic_command_fixed_delay():
	"""
	Test that we can construct a periodic command with a fixed initial
	delay.
	"""
	fd = schedule.PeriodicCommandFixedDelay.at_time(
		at = schedule.now(),
		delay = datetime.timedelta(seconds=2),
		target = lambda: None,
		)
	assert fd.due() is True
	assert fd.next().due() is False

class TestCommands(object):
	def test_delayed_command_from_timestamp(self):
		"""
		Ensure a delayed command can be constructed from a timestamp.
		"""
		t = time.time()
		do_nothing = lambda: None
		schedule.DelayedCommand.at_time(t, do_nothing)

	def test_command_at_noon(self):
		"""
		Create a periodic command that's run at noon every day.
		"""
		when = datetime.time(12, 0, tzinfo=pytz.utc)
		cmd = schedule.PeriodicCommandFixedDelay.daily_at(when, target=None)
		assert cmd.due() is False
		next_cmd = cmd.next()
		daily = datetime.timedelta(days=1)
		day_from_now = schedule.now() + daily
		two_days_from_now = day_from_now + daily
		assert day_from_now < next_cmd < two_days_from_now


class TestTimezones:
	def test_alternate_timezone_west(self):
		target_tz = pytz.timezone('US/Pacific')
		target = schedule.now().astimezone(target_tz)
		cmd = schedule.DelayedCommand.at_time(target, target=None)
		assert cmd.due()

	def test_alternate_timezone_east(self):
		target_tz = pytz.timezone('Europe/Amsterdam')
		target = schedule.now().astimezone(target_tz)
		cmd = schedule.DelayedCommand.at_time(target, target=None)
		assert cmd.due()
