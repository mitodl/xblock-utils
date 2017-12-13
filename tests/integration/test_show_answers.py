"""
Tests for ShowAnswerXBlockMixin
"""

import datetime
import ddt
import pytz
from xblock.core import XBlock
from xblock.fields import Integer, String, DateTime
from xblock.validation import ValidationMessage
from xblockutils.base_test import SeleniumXBlockTest
from xblockutils.constants import ShowAnswer
from xblockutils.show_answers import ShowAnswerXBlockMixin

from web_fragments.fragment import Fragment


class ShowAnswerXBlock(ShowAnswerXBlockMixin, XBlock):
    """
    A basic ShowAnswer XBlock implementation (for use in tests)
    """
    CATEGORY = 'showanswer'
    STUDIO_LABEL = 'Show Answers'

    color = String(default="red")
    count = Integer(default=42)
    comment = String(default="")
    date = DateTime(default=datetime.datetime(2014, 5, 14, tzinfo=pytz.UTC))
    editable_fields = ('color', 'count', 'comment', 'date')

    def student_view(self, context):
        return Fragment()


@ddt.ddt
class TestShowAnswerXBlock(SeleniumXBlockTest):
    """
    Test the Studio View created for ShowAnswerXBlock
    """

    def set_up_root_block(self, extra_args=''):
        self.set_scenario_xml('<showanswer {} />'.format(extra_args))
        self.go_to_view()
        return self.load_root_xblock()

    @XBlock.register_temp_plugin(ShowAnswerXBlock, "showanswer")
    def test_defaults(self):
        """
        Assert defaults
        """
        block = self.set_up_root_block()
        self.assertIsNone(block.solution)
        self.assertEqual(block.showanswer, ShowAnswer.PAST_DUE)

    @XBlock.register_temp_plugin(ShowAnswerXBlock, "showanswer")
    def test_fields(self):
        """
        Assert field overrides in XML
        """
        block = self.set_up_root_block('solution="The solution" showanswer="{}"'.format(ShowAnswer.ANSWERED))
        self.assertEqual(block.solution, 'The solution')
        self.assertEqual(block.showanswer, ShowAnswer.ANSWERED)
