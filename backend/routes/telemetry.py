import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from data_layer.data_loader import PatientStreamer

router = APIRouter()
streamer = PatientStreamer()

@router.websocket("/telemetry")
async def telemetry_stream(websocket: WebSocket):
    await websocket.accept()
    print("Dashboard connected to Telemetry Stream")
    
    # In a real startup production environment, you would manage active connections
    # and broadcast. For this MVP, we stream directly to the connected client.
    
    try:
        # We start the streamer for a patient (e.g., patient 100 for ECG, patient 03 for Vitals)
        stream_generator = streamer.stream_patient_data()
        
        while True:
            # Get the next chunk of data (simulating e.g., 50ms of data)
            data_chunk = next(stream_generator)
            
            # Send to frontend
            await websocket.send_text(json.dumps(data_chunk))
            
            # Control the stream rate to mimic real-time (e.g., 20 updates per sec)
            await asyncio.sleep(0.05)
            
    except WebSocketDisconnect:
        print("Dashboard disconnected")
    except StopIteration:
        print("End of patient recordings reached")
        await websocket.close()
    except Exception as e:
        print(f"Error in telemetry stream: {e}")
        await websocket.close()

@router.post("/api/scenario/{scenario_type}")
async def inject_scenario(scenario_type: str):
    """
    Allows the frontend to inject scenarios like 'Code Blue' or 'Stable'
    which alters the stream pointer to different patient datasets.
    """
    return streamer.set_scenario(scenario_type)
