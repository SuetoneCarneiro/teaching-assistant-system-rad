"""One module per feature, so each of us edits different files."""

from .actions import claim_question, close_question  # RF5, RF7 (Suetone)
from .create import QuestionCreateView  # RF3 (Pedro)
from .detail import AnswerView, QuestionDetailView  # RF6, RF9 (Suetone)
from .knowledge import knowledge_base  # RF8 (Pedro)
from .listing import QuestionListView  # RF4 (Suetone)
