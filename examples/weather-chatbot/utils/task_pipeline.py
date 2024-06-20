from pipecat.pipeline.pipeline import Pipeline
from pipecat.processors.aggregators.llm_response import LLMUserContextAggregator, LLMAssistantContextAggregator
from pipecat.processors.logger import FrameLogger


async def task_pipeline(context, llm, transport, tts):
    fl_in = FrameLogger("Inner")
    fl_out = FrameLogger("Outer")

    tma_in = LLMUserContextAggregator(context)
    tma_out = LLMAssistantContextAggregator(context)
    input_output = [
        fl_in,
        transport.input(),
        tma_in,
        llm,
        fl_out,
        tts,
        transport.output(),
        tma_out,
    ]
    return Pipeline(input_output)
