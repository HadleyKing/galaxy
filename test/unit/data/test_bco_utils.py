import json

from galaxy.model import WorkflowStep
from galaxy.model.orm.now import now
from galaxy.model.store._bco_convert_utils import SoftwarePrerequisteTracker
from galaxy.schema.bco import (
    BioComputeObjectCore,
    ContributionEnum,
    Contributor,
    DescriptionDomain,
    ErrorDomain,
    InputAndOutputDomain,
    ParametricDomain,
    PipelineStep,
    ProvenanceDomain,
    SPEC_VERSION,
    UsabilityDomain,
)
from galaxy.schema.bco.util import (
    extension_domains,
    galaxy_execution_domain,
    write_to_file,
)


def example_bc_core_object() -> BioComputeObjectCore:
    tags = ["rna"]
    pipeline_step = PipelineStep(
        step_number=1,
        name="step label",
        description="annotation",
        version="tool version",
        prerequisite=None,
        input_list=[],
        output_list=[],
    )
    description_domain = DescriptionDomain(
        keywords=tags,
        pipeline_steps=[pipeline_step],
        platform=["Galaxy"],
    )
    error_domain = ErrorDomain(
        empirical_error={},
        algorithmic_error={},
    )
    execution_domain = galaxy_execution_domain("https://usegalaxy.org")
    io_domain = InputAndOutputDomain(
        input_subdomain=[],
        output_subdomain=[],
    )
    contributor = Contributor(
        contribution=[ContributionEnum.contributedBy],
        name="Normal McNameHaver",
        email="normal@example.com",
        orcid="http://orcid.org/0000-0002-1825-0097",
    )
    parametric_domain = ParametricDomain(__root__=[])
    provenance_domain = ProvenanceDomain(
        name="workflow_name",
        version="workflow_version.0",
        review=[],
        created=now().isoformat(),
        modified=now().isoformat(),
        contributors=[contributor],
        license="MIT",
    )
    usability_domain = UsabilityDomain(__root__=["workflow annotation"])
    gx_extension_domains = extension_domains(
        galaxy_url="https://usegalaxy.org",
        galaxy_version="22.05.0",
    )
    core = BioComputeObjectCore(
        description_domain=description_domain,
        error_domain=error_domain,
        execution_domain=execution_domain,
        extension_domain=gx_extension_domains,
        io_domain=io_domain,
        parametric_domain=parametric_domain,
        provenance_domain=provenance_domain,
        usability_domain=usability_domain,
    )
    return core


def test_bco_writing(tmp_path):
    core_object = example_bc_core_object()
    output = tmp_path / "bco.json"
    object_id = "example id"
    write_to_file(object_id, core_object, output)
    with output.open() as f:
        final_bco_object = json.load(f)
    assert final_bco_object["spec_version"] == SPEC_VERSION
    assert final_bco_object["object_id"] == object_id


def test_software_prerequiste_tracker():
    tracker = SoftwarePrerequisteTracker()
    step_0 = WorkflowStep()
    step_0.tool_id = "toolshed.g2.bx.psu.edu/repos/devteam/fastqc/fastqc/0.73+galaxy0"
    step_0.type = "tool"
    step_0.tool_version = "0.73+galaxy0"
    step_1 = WorkflowStep()
    step_1.tool_id = "toolshed.g2.bx.psu.edu/repos/devteam/fastqc/fastqc/0.73+galaxy0"
    step_1.type = "tool"
    step_1.tool_version = "0.73+galaxy0"
    step_2 = WorkflowStep()
    step_2.tool_id = "toolshed.g2.bx.psu.edu/repos/iuc/compose_text_param/compose_text_param/0.1.1"
    step_2.type = "tool"
    step_2.tool_version = "0.1.1"

    # subworkflow step
    step_3 = WorkflowStep()
    step_3.type = "subworkflow"

    # stock tool
    step_4 = WorkflowStep()
    step_4.type = "tool"
    step_4.tool_id = "cat1"
    step_4.tool_version = "1.0.0"

    tracker.register_step(step_0)
    tracker.register_step(step_1)
    tracker.register_step(step_2)
    tracker.register_step(step_3)
    tracker.register_step(step_4)

    sps = tracker.software_prerequisites
    assert len(sps) == 3
