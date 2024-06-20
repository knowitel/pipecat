from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams
from pipecat.processors.aggregators.llm_response import LLMUserContextAggregator, LLMAssistantContextAggregator
from pipecat.processors.logger import FrameLogger


async def task_pipeline(context, llm, transport, tts):
    audio_frames_logger_in = FrameLogger("Inner")
    audio_frames_logger_out = FrameLogger("Outer")

    user_conversation_context = LLMUserContextAggregator(context)
    assistant_conversation_context = LLMAssistantContextAggregator(context)

    return Pipeline(
        processors=[
            # keep them in this order for now, otherwise the pipeline will break
            audio_frames_logger_in,
            transport.input(),
            user_conversation_context,
            llm,
            audio_frames_logger_out,
            tts,
            transport.output(),
            assistant_conversation_context
        ],
    )
