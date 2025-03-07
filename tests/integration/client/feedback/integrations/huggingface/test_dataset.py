#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import re
from uuid import uuid4

import argilla as rg
import pytest


@pytest.mark.skipif(os.getenv("HF_HUB_ACCESS_TOKEN") is None, reason="`HF_HUB_ACCESS_TOKEN` is not set")
class TestSuiteHuggingFaceDatasetMixin:
    @classmethod
    def setup_class(cls: "TestSuiteHuggingFaceDatasetMixin") -> None:
        github_ref_name = re.sub(r"[^a-zA-Z0-9-]", "-", os.getenv("GITHUB_REF_NAME", "fix/hello-world"))
        cls.repo_id = "argilla/test-integration-{}-{}".format(github_ref_name, uuid4())
        cls.dataset = rg.FeedbackDataset(
            fields=[
                rg.TextField(name="text-field", required=True),
                rg.TextField(name="optional-text-field", required=False),
            ],
            questions=[
                rg.TextQuestion(name="text-question", required=True),
                rg.RatingQuestion(name="rating-question", values=[1, 2, 3, 4, 5]),
                rg.LabelQuestion(name="label-question", labels=["A", "B", "C"]),
                rg.MultiLabelQuestion(name="multi-label-question", labels=["A", "B", "C", "D"], visible_labels=3),
                rg.RankingQuestion(name="ranking-question", values=["A", "B", "C"]),
            ],
            metadata_properties=[
                rg.TermsMetadataProperty(name="terms-metadata-property", values=["A", "B", "C"]),
                rg.IntegerMetadataProperty(name="integer-metadata-property", min=0, max=100),
                rg.FloatMetadataProperty(name="float-metadata-property", min=0.0, max=100.0),
            ],
            guidelines="These are the guidelines",
        )

        cls.dataset.add_records(
            [
                rg.FeedbackRecord(
                    fields={
                        "text-field": "This is a text field",
                        "optional-text-field": "This is an optional text field",
                    },
                    responses=[{"values": {"rating-question": {"value": 1}}, "status": "draft"}],
                    suggestions=[{"question_name": "text-question", "value": "This is a text response"}],
                    metadata={
                        "terms-metadata-property": "A",
                        "integer-metadata-property": 1,
                        "float-metadata-property": 1.0,
                    },
                    external_id="external-id-1",
                )
            ]
        )

    @classmethod
    def teardown_class(cls: "TestSuiteHuggingFaceDatasetMixin") -> None:
        from huggingface_hub import HfApi

        HfApi().delete_repo(cls.repo_id, repo_type="dataset", token=os.getenv("HF_HUB_ACCESS_TOKEN"))

    def test_push_to_huggingface(self) -> None:
        self.dataset.push_to_huggingface(repo_id=self.repo_id, private=True, token=os.getenv("HF_HUB_ACCESS_TOKEN"))

    def test_from_huggingface(self) -> None:
        dataset = rg.FeedbackDataset.from_huggingface(repo_id=self.repo_id, token=os.getenv("HF_HUB_ACCESS_TOKEN"))
        assert isinstance(dataset, rg.FeedbackDataset)
        assert dataset.fields == self.dataset.fields
        assert dataset.questions == self.dataset.questions
        assert dataset.metadata_properties == self.dataset.metadata_properties
        assert dataset.guidelines == self.dataset.guidelines
        assert dataset.records == self.dataset.records
