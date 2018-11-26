#include <chrono>
#include <dronecode_sdk/action.h>
#include <dronecode_sdk/dronecode_sdk.h>
#include <dronecode_sdk/offboard.h>
#include <dronecode_sdk/telemetry.h>
#include <iostream>

using namespace dronecode_sdk;
using std::this_thread::sleep_for;
using std::chrono::milliseconds;
using std::chrono::seconds;

int main()
{
    DronecodeSDK dc;
    std::string connection_url = "udp://127.0.0.1:14553" ;
    ConnectionResult connection_result;
    connection_result = dc.add_any_connection(connection_url);
    std::cout << "Vehile is connected" << connection_result << std::endl;

    while (!dc.is_connected()) 
    {
        std::cout << "Wait for system to connect via heartbeat" << std::endl;
        sleep_for(seconds(1));
    }

    System &system = dc.system();
    auto action = std::make_shared<Action>(system);
    std::cout << "System is ready" << std::endl;

    Action::Result arm_result = action->arm();
    std::cout << "Armed" << std::endl;

    sleep_for(sleep(3))

    Action::Result arm_result = action->disarm();
    std::cout << "Armed" << std::endl;

    return EXIT_SUCCESS;
}