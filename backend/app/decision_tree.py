"""Manual CART decision tree classifier using Gini impurity."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any


CATEGORICAL_FEATURES = {"Weekends"}
NUMERICAL_FEATURES = {"Sleep", "Meetings", "Stress"}
FEATURE_ORDER = ["Sleep", "Meetings", "Weekends", "Stress"]


def gini_impurity(labels: list[str]) -> float:
    """Compute Gini impurity: 1 - sum(p_i^2)."""
    if not labels:
        return 0.0
    counts = Counter(labels)
    total = len(labels)
    proportions_sq = sum((count / total) ** 2 for count in counts.values())
    return 1.0 - proportions_sq


def majority_class(labels: list[str]) -> str:
    return Counter(labels).most_common(1)[0][0]


def class_distribution(labels: list[str]) -> dict[str, int]:
    return dict(Counter(labels))


@dataclass
class TreeNode:
    """Serializable decision tree node."""

    node_type: str  # "internal" or "leaf"
    samples: int
    class_distribution: dict[str, int]
    predicted_class: str
    gini: float
    feature: str | None = None
    operator: str | None = None
    threshold: float | None = None
    category_value: str | None = None
    left: TreeNode | None = None
    right: TreeNode | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "type": self.node_type,
            "samples": self.samples,
            "class_distribution": self.class_distribution,
            "predicted_class": self.predicted_class,
            "gini": round(self.gini, 6),
        }
        if self.node_type == "internal":
            payload.update(
                {
                    "feature": self.feature,
                    "operator": self.operator,
                    "threshold": self.threshold,
                    "category_value": self.category_value,
                    "left": self.left.to_dict() if self.left else None,
                    "right": self.right.to_dict() if self.right else None,
                }
            )
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TreeNode:
        node = cls(
            node_type=data["type"],
            samples=data["samples"],
            class_distribution=data["class_distribution"],
            predicted_class=data["predicted_class"],
            gini=data["gini"],
            feature=data.get("feature"),
            operator=data.get("operator"),
            threshold=data.get("threshold"),
            category_value=data.get("category_value"),
        )
        if data["type"] == "internal":
            left = data.get("left")
            right = data.get("right")
            node.left = cls.from_dict(left) if left else None
            node.right = cls.from_dict(right) if right else None
        return node


@dataclass
class SplitCandidate:
    feature: str
    operator: str
    threshold: float | None
    category_value: str | None
    left_indices: list[int]
    right_indices: list[int]
    weighted_gini: float


class DecisionTreeClassifier:
    """CART classifier with Gini impurity ÔÇö no external ML libraries."""

    def __init__(
        self,
        max_depth: int = 8,
        min_samples_split: int = 2,
    ) -> None:
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root: TreeNode | None = None
        self.feature_names: list[str] = []
        self.target_classes: list[str] = []

    def fit(self, rows: list[dict[str, Any]], feature_names: list[str]) -> TreeNode:
        self.feature_names = feature_names
        labels = [str(row["Target"]) for row in rows]
        self.target_classes = sorted(set(labels))
        indices = list(range(len(rows)))
        self.root = self._build_tree(rows, indices, depth=0)
        return self.root

    def _build_tree(
        self,
        rows: list[dict[str, Any]],
        indices: list[int],
        depth: int,
    ) -> TreeNode:
        labels = [str(rows[i]["Target"]) for i in indices]
        dist = class_distribution(labels)
        current_gini = gini_impurity(labels)
        predicted = majority_class(labels)

        # Stopping: pure node, max depth, or too few samples to split
        if len(set(labels)) == 1:
            return TreeNode(
                node_type="leaf",
                samples=len(indices),
                class_distribution=dist,
                predicted_class=predicted,
                gini=current_gini,
            )

        if depth >= self.max_depth or len(indices) < self.min_samples_split:
            return TreeNode(
                node_type="leaf",
                samples=len(indices),
                class_distribution=dist,
                predicted_class=predicted,
                gini=current_gini,
            )

        best_split = self._find_best_split(rows, indices)
        if best_split is None:
            # No candidate split reduces Gini impurity ÔÇö stop as a leaf.
            return TreeNode(
                node_type="leaf",
                samples=len(indices),
                class_distribution=dist,
                predicted_class=predicted,
                gini=current_gini,
            )

        left_node = self._build_tree(rows, best_split.left_indices, depth + 1)
        right_node = self._build_tree(rows, best_split.right_indices, depth + 1)

        return TreeNode(
            node_type="internal",
            samples=len(indices),
            class_distribution=dist,
            predicted_class=predicted,
            gini=current_gini,
            feature=best_split.feature,
            operator=best_split.operator,
            threshold=best_split.threshold,
            category_value=best_split.category_value,
            left=left_node,
            right=right_node,
        )

    def _find_best_split(
        self,
        rows: list[dict[str, Any]],
        indices: list[int],
    ) -> SplitCandidate | None:
        labels = [str(rows[i]["Target"]) for i in indices]
        parent_gini = gini_impurity(labels)
        total = len(indices)
        best: SplitCandidate | None = None

        for feature in self.feature_names:
            if feature in CATEGORICAL_FEATURES:
                candidate = self._evaluate_categorical_split(rows, indices, feature, total)
            else:
                candidate = self._evaluate_numerical_split(rows, indices, feature, total)

            if candidate is None:
                continue

            # Keep only splits that strictly reduce parent impurity.
            if candidate.weighted_gini >= parent_gini:
                continue

            if best is None or candidate.weighted_gini < best.weighted_gini:
                best = candidate

        return best

    def _evaluate_numerical_split(
        self,
        rows: list[dict[str, Any]],
        indices: list[int],
        feature: str,
        total: int,
    ) -> SplitCandidate | None:
        values = sorted({float(rows[i][feature]) for i in indices})
        if len(values) <= 1:
            return None

        thresholds = [(values[i] + values[i + 1]) / 2 for i in range(len(values) - 1)]
        best: SplitCandidate | None = None

        for threshold in thresholds:
            left_indices: list[int] = []
            right_indices: list[int] = []
            for idx in indices:
                if float(rows[idx][feature]) <= threshold:
                    left_indices.append(idx)
                else:
                    right_indices.append(idx)

            # Skip degenerate splits that send all samples to one side.
            if not left_indices or not right_indices:
                continue

            weighted = self._weighted_gini(rows, left_indices, right_indices, total)
            candidate = SplitCandidate(
                feature=feature,
                operator="<=",
                threshold=threshold,
                category_value=None,
                left_indices=left_indices,
                right_indices=right_indices,
                weighted_gini=weighted,
            )
            if best is None or weighted < best.weighted_gini:
                best = candidate

        return best

    def _evaluate_categorical_split(
        self,
        rows: list[dict[str, Any]],
        indices: list[int],
        feature: str,
        total: int,
    ) -> SplitCandidate | None:
        categories = sorted({str(rows[i][feature]).strip().upper() for i in indices})
        if len(categories) <= 1:
            return None

        best: SplitCandidate | None = None
        for category in categories:
            left_indices: list[int] = []
            right_indices: list[int] = []
            for idx in indices:
                if str(rows[idx][feature]).strip().upper() == category:
                    left_indices.append(idx)
                else:
                    right_indices.append(idx)

            if not left_indices or not right_indices:
                continue

            weighted = self._weighted_gini(rows, left_indices, right_indices, total)
            candidate = SplitCandidate(
                feature=feature,
                operator="==",
                threshold=None,
                category_value=category,
                left_indices=left_indices,
                right_indices=right_indices,
                weighted_gini=weighted,
            )
            if best is None or weighted < best.weighted_gini:
                best = candidate

        return best

    def _weighted_gini(
        self,
        rows: list[dict[str, Any]],
        left_indices: list[int],
        right_indices: list[int],
        total: int,
    ) -> float:
        """Weighted average Gini after a split."""
        left_labels = [str(rows[i]["Target"]) for i in left_indices]
        right_labels = [str(rows[i]["Target"]) for i in right_indices]
        left_weight = len(left_indices) / total
        right_weight = len(right_indices) / total
        return left_weight * gini_impurity(left_labels) + right_weight * gini_impurity(right_labels)

    def predict_one(self, sample: dict[str, Any]) -> tuple[str, list[str]]:
        if self.root is None:
            raise ValueError("Tree has not been trained yet.")
        return self._traverse(self.root, sample, [])

    def _traverse(
        self,
        node: TreeNode,
        sample: dict[str, Any],
        path: list[str],
    ) -> tuple[str, list[str]]:
        if node.node_type == "leaf":
            path.append(f"leaf: {node.predicted_class}")
            return node.predicted_class, path

        feature = node.feature
        assert feature is not None

        if node.operator == "<=":
            value = float(sample[feature])
            threshold = node.threshold
            assert threshold is not None
            condition = f"{feature} <= {threshold:g}"
            if value <= threshold:
                path.append(condition)
                return self._traverse(node.left, sample, path) if node.left else (node.predicted_class, path)
            path.append(f"{feature} > {threshold:g}")
            return self._traverse(node.right, sample, path) if node.right else (node.predicted_class, path)

        category = node.category_value
        assert category is not None
        sample_value = str(sample[feature]).strip().upper()
        condition = f"{feature} == {category}"
        if sample_value == category:
            path.append(condition)
            return self._traverse(node.left, sample, path) if node.left else (node.predicted_class, path)
        path.append(f"{feature} != {category}")
        return self._traverse(node.right, sample, path) if node.right else (node.predicted_class, path)

    def to_json(self) -> dict[str, Any]:
        if self.root is None:
            raise ValueError("Tree has not been trained yet.")
        return self.root.to_dict()

    def load_from_json(self, tree_dict: dict[str, Any]) -> None:
        self.root = TreeNode.from_dict(tree_dict)
