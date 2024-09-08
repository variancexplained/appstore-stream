#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/identity/passport.py                                                #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday July 24th 2024 12:42:51 am                                                #
# Modified   : Saturday September 7th 2024 06:25:19 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Identity Module"""
from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Union

from appvocai.application.orchestration.job import Job
from appvocai.application.orchestration.project import Project
from appvocai.application.orchestration.task import Task
from appvocai.core.data import IMMUTABLE_TYPES, SEQUENCE_TYPES
from appvocai.core.enum import Category, DataType, Env
from appvocai.domain.artifact.base import Artifact
from appvocai.infra.base.config import Config
from appvocai.infra.identity.idxgen import IDXGen
from appvocai.toolkit.date import ThirdDateFormatter

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
idxgen = IDXGen()
# ------------------------------------------------------------------------------------------------ #
dt4mat = ThirdDateFormatter()


# ------------------------------------------------------------------------------------------------ #
class Passport:
    """
    A class to represent a passport identity for artifacts within the system.

    The `Passport` class encapsulates the creation and environment information for artifacts,
    providing methods for object representation (`__repr__`) and string formatting (`__str__`).

    Attributes:
    ----------
    dt_created : datetime
        The timestamp when the passport object was created. Automatically set to the current time.

    environment : Env
        The environment instance (e.g., development, production) for which this passport is relevant.
        It is retrieved from the configuration using the `Config` class and an `Env` instance.

    Methods:
    -------
    __repr__() -> str
        Returns a detailed string representation of the object for debugging and logging purposes.
        It includes only immutable attribute types for clarity.

    __str__() -> str
        Returns a nicely formatted string representation of the object's data, displaying each attribute
        and its value. Only immutable types are displayed for simplicity.

    as_dict() -> Dict[str, Any]
        This method should return the object's attributes as a dictionary, allowing for further manipulation or display.
    """

    def __init__(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        """
        Initializes the Passport object with creation time and environment information.

        Parameters:
        ----------
        *args : Any
            Variable length argument list, passed through the initializer.

        **kwargs : Dict[str, Any]
            Arbitrary keyword arguments passed through the initializer.
        """
        self.dt_created = datetime.now()

        # Get current environment from config and obtain an Env instance.
        env = Config().get_environment()
        self.environment = Env.get(value=env)

    def __repr__(self) -> str:
        """
        Provides a detailed string representation of the object, including only immutable attributes.

        Returns:
        -------
        str
            The formatted string representation of the object for debugging.
        """
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(
                "{}={!r}".format(k, v)
                for k, v in self.__dict__.items()
                if type(v) in IMMUTABLE_TYPES
            ),
        )

    def __str__(self) -> str:
        """
        Returns a formatted string version of the object's data, displaying attributes and their values.

        The width for formatting is controlled to ensure readability, and only immutable types are displayed.

        Returns:
        -------
        str
            The human-readable string representation of the object.
        """
        width = 32
        breadth = width * 2
        s = f"\n\n{self.__class__.__name__.center(breadth, ' ')}"
        d = self.as_dict()
        for k, v in d.items():
            if type(v) in IMMUTABLE_TYPES:
                s += f"\n{k.rjust(width,' ')} | {v}"
        s += "\n\n"
        return s

    def as_dict(self) -> Dict[str, Union[str, int, float, datetime, None]]:
        """Returns a dictionary representation of the the Config object."""
        return {
            k: self._export_config(v)
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        }

    @classmethod
    def _export_config(
        cls,
        v: Any,
    ) -> Any:  # pragma: no cover
        """Returns v with Configs converted to dicts, recursively."""
        if isinstance(v, IMMUTABLE_TYPES):
            return v
        elif isinstance(v, SEQUENCE_TYPES):
            return type(v)(map(cls._export_config, v))
        elif isinstance(v, dict):
            return v
        elif hasattr(v, "as_dict"):
            return v.as_dict()
        elif isinstance(v, Enum):
            return v.value
        elif isinstance(v, datetime):
            return v.isoformat()
        else:
            return dict()


# ------------------------------------------------------------------------------------------------ #
class ProjectPassport(Passport):
    """
    A class that represents the identity of a project, inheriting from the base Passport class.

    The `ProjectPassport` class provides a unique identity for projects, including attributes such as
    project ID, category, data type, and project owner. The name of the project is automatically
    generated using the owner's class name, data type, category, creation date, and a sequential project ID.

    Attributes:
    ----------
    project_id : int
        A unique identifier for the project, generated sequentially by `idxgen.next_idx`.

    category : Category
        The category to which the project belongs (e.g., Books, Games). Provided during initialization.

    data_type : DataType
        The type of data being handled by the project (e.g., AppData, ReviewData). Provided during initialization.

    name : str
        The autogenerated name for the project, following the pattern:
        `OwnerClassName-DataType-Category-YYYYMMDD-ProjectID`.
        Example: `Project-AppData-Books-20240809-44`.

    owner : Project
        The project owner object. The owner's class name is used in the autogenerated name.

    Methods:
    -------
    __init__(owner: Type, category: Category, data_type: Data -> None
        Initializes the project passport with a unique project ID, category, data type,
        and owner, and generates a name based on these attributes and the creation date.
    """

    def __init__(self, owner: Project, category: Category, data_type: DataType) -> None:
        """
        Initializes the ProjectPassport object with an owner, category, and data type.

        Parameters:
        ----------
        owner : Project
            The project owner object, whose class name will be part of the autogenerated project name.

        category : Category
            The category to which the project belongs (e.g., Books, Games).

        data_type : DataType
            The type of data being handled by the project (e.g., AppData, ReviewData).
        """
        super().__init__()
        self.project_id = idxgen.next_idx
        self.category = category
        self.data_type = data_type
        self.dt_created = datetime.now()
        self.name = f"{owner.__class__.__name__}-{self.data_type.value}-{self.category.value}-{self.project_id}"


# ------------------------------------------------------------------------------------------------ #
class JobPassport(Passport):
    """
    A class that represents the identity of a job, inheriting from the base Passport class.

    The `JobPassport` class provides a unique identity for jobs, including attributes such as job ID,
    project ID, category, data type, and creator. The name of the job is automatically generated using
    the owner's class name, data type, category, creation date, and a sequential job ID.

    Attributes:
    ----------
    job_id : int
        A unique identifier for the job, generated sequentially by `idxgen.next_idx`.

    project_id : int
        The ID of the project to which this job belongs, derived from the `ProjectPassport`.

    category : Category
        The category of the job, inherited from the project through the `ProjectPassport`.

    data_type : DataType
        The type of data being handled by the job, inherited from the project through the `ProjectPassport`.

    name : str
        The autogenerated name for the job, following the pattern:
        `OwnerClassName-DataType-Category-YYYYMMDD-JobID`.
        Example: `Job-AppData-Books-20240809-44`.

    creator : ProjectPassport
        The project passport that serves as the creator of this job, linking it to the parent project.

    Methods:
    -------
    __init__(owner: Type, project_passport: ProjectPassport) -> None
        Initializes the job passport with a unique job ID, project ID, category, data type,
        and creator, and generates a name based on these attributes and the creation date.
    """

    def __init__(self, owner: Job, project_passport: ProjectPassport) -> None:
        """
        Initializes the JobPassport object with an owner and a reference to the project passport.

        Parameters:
        ----------
        owner : Job
            The job owner object, whose class name will be part of the autogenerated job name.

        project_passport : ProjectPassport
            The passport of the project to which this job belongs, providing access to project ID, category,
            and data type for use in the job passport.
        """
        super().__init__()
        self.job_id = idxgen.next_idx
        self.project_id = project_passport.project_id
        self.category = project_passport.category
        self.data_type = project_passport.data_type
        self.dt_created = datetime.now()
        self.name = f"{owner.__class__.__name__}-{self.data_type.value}-{self.category.value}-{self.job_id}"
        self.creator = project_passport


# ------------------------------------------------------------------------------------------------ #
class TaskPassport(Passport):
    """
    A class that represents the identity of a task, inheriting from the base Passport class.

    The `TaskPassport` class provides a unique identity for tasks, including attributes such as task ID,
    job ID, project ID, category, data type, and creator. The name of the task is automatically generated
    using the owner's class name, data type, category, creation date, and a sequential task ID.

    Attributes:
    ----------
    task_id : int
        A unique identifier for the task, generated sequentially by `idxgen.next_idx`.

    job_id : int
        The ID of the job to which this task belongs, derived from the `JobPassport`.

    project_id : int
        The ID of the project to which this task belongs, inherited from the `JobPassport` and ultimately
        from the `ProjectPassport`.

    category : Category
        The category of the task, inherited from the job through the `JobPassport`.

    data_type : DataType
        The type of data being handled by the task, inherited from the job through the `JobPassport`.

    name : str
        The autogenerated name for the task, following the pattern:
        `OwnerClassName-DataType-Category-YYYYMMDD-TaskID`.
        Example: `Task-AppData-Books-20240809-44`.

    creator : JobPassport
        The job passport that serves as the creator of this task, linking it to the parent job.

    Methods:
    -------
    __init__(owner: Type, job_passport: JobPassport) -> None
        Initializes the task passport with a unique task ID, job ID, project ID, category, data type,
        and creator, and generates a name based on these attributes and the creation date.
    """

    def __init__(self, owner: Task, job_passport: JobPassport) -> None:
        """
        Initializes the TaskPassport object with an owner and a reference to the job passport.

        Parameters:
        ----------
        owner : Task
            The task owner object, whose class name will be part of the autogenerated task name.

        job_passport : JobPassport
            The passport of the job to which this task belongs, providing access to job ID, project ID,
            category, and data type for use in the task passport.
        """
        super().__init__()
        self.task_id = idxgen.next_idx
        self.job_id = job_passport.job_id
        self.project_id = job_passport.project_id
        self.category = job_passport.category
        self.data_type = job_passport.data_type
        self.dt_created = datetime.now()
        self.name = f"{owner.__class__.__name__}-{self.data_type.value}-{self.category.value}-{self.task_id}"
        self.creator = job_passport


# ------------------------------------------------------------------------------------------------ #
class OperationPassport(Passport):
    """
    Represents a passport for an operation within a task, inheriting from the base `Passport` class.

    This class is used to uniquely identify and encapsulate metadata related to a specific operation
    within the context of a task. The `OperationPassport` stores IDs for the operation, task, job, project,
    as well as details such as the category, data type, and creation timestamp. It also retains the
    `TaskPassport` that initiated the operation, providing a link back to the task-level information.

    Attributes:
    -----------
    operation_id : str
        A unique identifier for the operation, generated using `idxgen.next_idx`.
    task_id : str
        The ID of the task associated with this operation, derived from the `task_passport`.
    job_id : str
        The ID of the job associated with this operation, derived from the `task_passport`.
    project_id : str
        The ID of the project associated with this operation, derived from the `task_passport`.
    category : Enum
        The category of the task (or operation) being executed, derived from the `task_passport`.
    data_type : Enum
        The type of data being processed during the task or operation, derived from the `task_passport`.
    operation_type : str
        The name of the class (`owner`), representing the type of operation being performed.
    dt_created : str
        The ISO 8601 formatted timestamp of when the operation was created.
    name : str
        A human-readable name for the operation, constructed using the operation type, data type, category,
        and task ID.
    creator : TaskPassport
        The `TaskPassport` object representing the task that initiated this operation.
    """

    def __init__(self, owner: Task, task_passport: TaskPassport) -> None:
        """
        Initializes an `OperationPassport` instance with metadata about the operation.

        Parameters:
        -----------
        owner : Task
            The task object that owns this operation, used to derive the operation type.
        task_passport : TaskPassport
            The `TaskPassport` object containing task-level metadata such as task ID, job ID, project ID,
            category, and data type.

        The `OperationPassport` is constructed by copying relevant IDs and metadata from the `task_passport`
        and generating a unique `operation_id`. It also captures the time the operation was created, and
        assigns a human-readable name to the operation.
        """
        super().__init__()
        self.operation_id = idxgen.next_idx
        self.task_id = task_passport.task_id
        self.job_id = task_passport.job_id
        self.project_id = task_passport.project_id
        self.category = task_passport.category
        self.data_type = task_passport.data_type
        self.operation_type = owner.__class__.__name__
        self.dt_created = datetime.now()
        self.name = f"{owner.__class__.__name__}-{self.data_type.value}-{self.category.value}-{self.task_id}"
        self.creator = task_passport


# ------------------------------------------------------------------------------------------------ #
class ArtifactPassport(Passport):
    """
    A class that represents the identity of an artifact, inheriting from the base Passport class.

    The `ArtifactPassport` class provides a unique identity for artifacts, including attributes such as task ID,
    job ID, project ID, category, data type, and creator. The name of the artifact is automatically generated
    using the owner's class name, data type, category, creation date, and a sequential task ID.

    Attributes:
    ----------
    artifact_id: int
        A unique identifier for the artifact. This is an autogenerated sequential integer.

    task_id : int
        The ID of the task to which this artifact belongs, derived from the `TaskPassport`.

    job_id : int
        The ID of the job to which this artifact belongs, inherited from the `TaskPassport` and `JobPassport`.

    project_id : int
        The ID of the project to which this artifact belongs, inherited from the `TaskPassport` and `ProjectPassport`.

    category : Category
        The category of the artifact, inherited from the task through the `TaskPassport`.

    data_type : DataType
        The type of data being handled by the artifact, inherited from the task through the `TaskPassport`.

    operation_type: OperationType
        Artifacts are 'stamped' with the operation type as it enters the operation object. Operation
        type is an essential data element for performance analysis.

    name : str
        The autogenerated name for the artifact, following the pattern:
        `OwnerClassName-DataType-Category-YYYYMMDD-TaskID`.
        Example: `Artifact-AppData-Books-20240809-44`.

    creator : TaskPassport
        The task passport that serves as the creator of this artifact, linking it to the parent task.

    Methods:
    -------
    __init__(owner: Type, task_passport: TaskPassport) -> None
        Initializes the artifact passport with a unique task ID, job ID, project ID, category, data type,
        and creator, and generates a name based on these attributes and the creation date.
    """

    def __init__(self, owner: Artifact, operation_passport: OperationPassport) -> None:
        """
        Initializes the ArtifactPassport object with an owner and a reference to the task passport.

        Parameters:
        ----------
        owner : Artifact
            The artifact owner object, whose class name will be part of the autogenerated artifact name.

        task_passport : TaskPassport
            The passport of the task to which this artifact belongs, providing access to task ID, job ID,
            project ID, category, and data type for use in the artifact passport.
        """
        super().__init__()
        self.artifact_id = idxgen.next_idx
        self.operation_id = operation_passport.operation_id
        self.job_id = operation_passport.job_id
        self.project_id = operation_passport.project_id
        self.task_id = operation_passport.task_id
        self.category = operation_passport.category
        self.data_type = operation_passport.data_type
        self.operation_type = operation_passport.operation_type
        self.dt_created = datetime.now()
        self.name = f"{owner.__class__.__name__}-{self.data_type.value}-{self.category.value}-{self.task_id}"
        self.creator = operation_passport
