"""Container for Pymordial UI elements representing a screen."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from uuid import uuid4

from pymordial.ui.element import PymordialElement
from pymordial.utils.exceptions import ElementNotFoundError


@dataclass(eq=False)
class PymordialScreen:
    """Represents a screen within an application.

    Attributes:
        name: The name of the screen.
        elements: A dictionary of elements belonging to this screen.
        screen_id: Unique identifier for this screen instance (auto-generated).
    """

    name: str
    elements: dict[str, PymordialElement] = field(default_factory=dict)
    screen_id: str = field(default_factory=lambda: str(uuid4()), init=False)

    def __post_init__(self) -> None:
        """Validates the screen attributes after initialization.

        Raises:
            ValueError: If the name is empty or not a string.
            TypeError: If elements is not a dictionary or contains invalid keys/values.
        """
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Screen name must be a non-empty string")

        if not isinstance(self.elements, dict):
            raise TypeError("Elements must be a dictionary")

        for key, element in self.elements.items():
            if not isinstance(key, str):
                raise TypeError(
                    f"Element keys must be strings, got {type(key).__name__}"
                )
            if not isinstance(element, PymordialElement):
                raise TypeError(
                    f"Values must be PymordialElement instances, got {type(element).__name__}"
                )

    def add_element(self, element: PymordialElement) -> None:
        """Adds an element to the screen.

        Args:
            element: The element to add.

        Raises:
            TypeError: If the element is not a PymordialElement instance.
            ValueError: If an element with the same label already exists.
        """
        if not isinstance(element, PymordialElement):
            raise TypeError(
                f"Element must be a PymordialElement instance, got {type(element).__name__}"
            )
        if element.label in self.elements:
            raise ValueError(f"Element with label '{element.label}' already exists")
        self.elements[element.label] = element

    def is_current_screen(
        self,
        is_visible: Callable[[PymordialElement], bool],
        elements: Iterable[PymordialElement] | None = None,
    ) -> bool:
        """Checks whether this screen is the one currently displayed.

        Asks the caller-supplied visibility check about each identifying
        element. Pass ``controller.is_element_visible`` as ``is_visible``;
        the screen takes a callable instead of a controller so this module
        never imports the controller layer.

        Args:
            is_visible: Callable that takes an element and returns True
                when it is currently visible on screen.
            elements: Elements that identify this screen. Defaults to all
                registered elements.

        Returns:
            True if every checked element is visible, False otherwise.
            False when there are no elements to check: an empty screen
            cannot identify itself.
        """
        to_check = (
            list(elements) if elements is not None else list(self.elements.values())
        )
        if not to_check:
            return False
        return all(is_visible(element) for element in to_check)

    def get_element(self, label: str) -> PymordialElement:
        """Retrieves an element by its label.

        Args:
            label: The label of the element to retrieve.

        Returns:
            The PymordialElement instance.

        Raises:
            ElementNotFoundError: If the element is not found.
        """
        try:
            return self.elements[label]
        except KeyError:
            raise ElementNotFoundError(
                f"Element '{label}' not found as element of screen '{self.name}'"
            )

    def remove_element(self, label: str) -> PymordialElement:
        """Removes an element by its label.

        Args:
            label: The label of the element to remove.

        Returns:
            The removed PymordialElement.

        Raises:
            ElementNotFoundError: If the element is not found.
        """
        try:
            return self.elements.pop(label)
        except KeyError:
            raise ElementNotFoundError(
                f"Element '{label}' not found on screen '{self.name}'"
            )

    def __hash__(self) -> int:
        """Returns hash based on unique screen_id."""
        return hash(self.screen_id)

    def __eq__(self, other) -> bool:
        """Compares screens by their unique screen_id."""
        if not isinstance(other, PymordialScreen):
            return NotImplemented
        return self.screen_id == other.screen_id
