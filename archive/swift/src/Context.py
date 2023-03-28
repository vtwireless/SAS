class Context:
    """
    Interface for the context information template that will be used by all member blocks
    """

    cbsd_id: int
    secondary_user_type: str
    target_band: str
    location: str
    mobile: bool
    data_type: str
    start_time: int
    duration: int

    def __init__(self, **kwargs):
        self.cbsdId = kwargs.get("cbsd_id", None)

