from pydantic import BaseModel
from pyosc import OSCString, OSCArg, OSCFloat


class ActiveCueValidator(BaseModel):
    address: str
    args: tuple[OSCArg, ...]

    @property
    def cue_number(self) -> str:
        return self.address.split("/")[6]

    @property
    def cue_list(self) -> str:
        return self.address.split("/")[5]

    @property
    def cue_note(self) -> str:
        if isinstance(self.args[27], OSCString):
            return self.args[27].value
        raise ValueError("Cue note argument is not a string or is missing.")


class ActiveCueNumberValidator(BaseModel):
    address: str
    args: tuple[OSCFloat]

    @property
    def number(self) -> float:
        splits = self.address.split("/")
        return float(splits[6])

    @property
    def list(self) -> float:
        splits = self.address.split("/")
        return float(splits[5])

    @property
    def completion(self) -> float:
        return self.args[0].value * 100


class ActiveCompletionValidator(BaseModel):
    args: tuple[OSCFloat]

    @property
    def completion(self) -> float:
        return self.args[0].value * 100
