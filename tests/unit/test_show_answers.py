"""Tests for ShowAnswerXBlockMixin"""
import mock
from unittest import TestCase

import ddt
from workbench.runtime import WorkbenchRuntime
from xblock.core import XBlock

from tests.integration.test_show_answers import ShowAnswerXBlock
from xblockutils.constants import ShowAnswer


@ddt.ddt
class TestShowAnswerXBlock(TestCase):
    """
    Unit tests for ShowAnswerXBlockMixin
    """

    def get_root(self):
        self.runtime = WorkbenchRuntime()
        self.root_id = self.runtime.parse_xml_string('<showanswer />')
        return self.runtime.get_block(self.root_id)

    @ddt.data(*[
        [True, True, True],
        [True, False, False],
        [False, True, True],
        [False, False, True],
    ])
    @ddt.unpack
    @XBlock.register_temp_plugin(ShowAnswerXBlock, "showanswer")
    def test_closed(self, can_attempt, past_due, expected):
        """
        Assert possible values for closed()
        """
        block = self.get_root()
        with mock.patch.object(
            ShowAnswerXBlock, 'can_attempt', return_value=can_attempt,
        ), mock.patch.object(
            ShowAnswerXBlock, 'is_past_due', return_value=past_due,
        ):
            self.assertEqual(block.closed(), expected)

    @XBlock.register_temp_plugin(ShowAnswerXBlock, "showanswer")
    def test_answer_available_no_correctness(self):
        """
        If no correctness is available, the answer is not available
        """
        block = self.get_root()
        with mock.patch.object(
            ShowAnswerXBlock, 'correctness_available', return_value=False
        ):
            self.assertFalse(block.answer_available())

    @XBlock.register_temp_plugin(ShowAnswerXBlock, "showanswer")
    def test_answer_available_user_is_staff(self):
        """
        If user is staff and correctness is available, the answer is available
        """
        block = self.get_root()
        self.runtime.user_is_staff = True
        with mock.patch.object(
            ShowAnswerXBlock, 'correctness_available', return_value=True
        ), mock.patch.object(
            ShowAnswerXBlock, 'runtime_user_is_staff', return_value=True,
        ):
            self.assertTrue(block.answer_available())

    @ddt.data(*[
        ['', {}, False],
        [ShowAnswer.NEVER, {}, False],
        [ShowAnswer.ATTEMPTED, {}, False],
        [ShowAnswer.ATTEMPTED, {'has_attempted': True}, True],
        [ShowAnswer.ANSWERED, {}, False],
        [ShowAnswer.ANSWERED, {'is_correct': True}, True],
        [ShowAnswer.CLOSED, {}, False],
        [ShowAnswer.CLOSED, {'closed': True}, True],
        [ShowAnswer.FINISHED, {}, False],
        [ShowAnswer.FINISHED, {'closed': True}, True],
        [ShowAnswer.FINISHED, {'is_correct': True}, True],
        [ShowAnswer.FINISHED, {'closed': True, 'is_correct': True}, True],
        [ShowAnswer.CORRECT_OR_PAST_DUE, {}, False],
        [ShowAnswer.CORRECT_OR_PAST_DUE, {'is_correct': True}, True],
        [ShowAnswer.CORRECT_OR_PAST_DUE, {'is_past_due': True}, True],
        [ShowAnswer.CORRECT_OR_PAST_DUE, {'is_correct': True, 'is_past_due': True}, True],
        [ShowAnswer.PAST_DUE, {}, False],
        [ShowAnswer.PAST_DUE, {'is_past_due': True}, True],
        [ShowAnswer.ALWAYS, {}, True],
        ['unexpected', {}, False],
    ])
    @ddt.unpack
    @XBlock.register_temp_plugin(ShowAnswerXBlock, "showanswer")
    def test_answer_available_showanswer(self, showanswer, properties, expected):
        """
        Try different values of showanswer and assert answer_available()
        """
        block = self.get_root()
        block.showanswer = showanswer
        with mock.patch.object(
            ShowAnswerXBlock, 'correctness_available', return_value=True,
        ), mock.patch.object(
            ShowAnswerXBlock, 'runtime_user_is_staff', return_value=False,
        ), mock.patch.object(
            ShowAnswerXBlock, 'has_attempted', return_value=properties.get('has_attempted', False),
        ), mock.patch.object(
            ShowAnswerXBlock, 'is_correct', return_value=properties.get('is_correct', False),
        ), mock.patch.object(
            ShowAnswerXBlock, 'closed', return_value=properties.get('closed', False),
        ), mock.patch.object(
            ShowAnswerXBlock, 'is_past_due', return_value=properties.get('is_past_due', False),
        ):
            self.assertEqual(block.answer_available(), expected)
