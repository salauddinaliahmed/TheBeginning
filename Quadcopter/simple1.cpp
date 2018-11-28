// Simple example to demonstrate how to use the Dronecode SDK.
// Author: Julian Oes <julian@oes.ch>

#include <chrono>
#include <cstdint>
#include <dronecode_sdk/system.h>
#include <dronecode_sdk/action.h>
#include <dronecode_sdk/dronecode_sdk.h>
#include <dronecode_sdk/telemetry.h>
#include <iostream>
#include <thread>

using namespace dronecode_sdk;
using namespace std::this_thread;
using namespace std::chrono;
using namespace std;

template <typename T> class type_name {
public:
    static const char *name;
};

#define DECLARE_TYPE_NAME(x) template<> const char *type_name<x>::name = #x;
#define GET_TYPE_NAME(x) (type_name<typeof(x)>::name)

#define ERROR_CONSOLE_TEXT "\033[31m" // Turn text on console red
#define TELEMETRY_CONSOLE_TEXT "\033[34m" // Turn text on console blue
#define NORMAL_CONSOLE_TEXT "\033[0m" // Restore normal console colour



void usage(std::string bin_name)
{
    std::cout << NORMAL_CONSOLE_TEXT << "Usage : " << bin_name << " <connection_url>" << std::endl
              << "Connection URL format should be :" << std::endl
              << " For TCP : tcp://[server_host][:server_port]" << std::endl
              << " For UDP : udp://[bind_host][:bind_port]" << std::endl
              << " For Serial : serial:///path/to/serial/dev[:baudrate]" << std::endl
              << "For example, to connect to the simulator use URL: udp://:14540" << std::endl;
}

void component_discovered(ComponentType component_type)
{
    std::cout << NORMAL_CONSOLE_TEXT << "Discovered a component: " << unsigned(component_type) << std::endl;

}
int main(int argc, char **argv)
{
    std::cout << "Argc: " << argc << "\n" <<"Arguments: " << std::endl;
    for (int i = 0; i < argc; ++i)
    {
        std::cout << argv[i] << std::endl;
   }
    DronecodeSDK dc;
    std::string connection_url = "udp://127.0.0.1:14553";
    ConnectionResult connection_result;
    connection_result = dc.add_any_connection(connection_url);
    if (connection_result != ConnectionResult::SUCCESS) {
        std::cout << ERROR_CONSOLE_TEXT << "Connection failed: " << connection_result_str(connection_result) << NORMAL_CONSOLE_TEXT << std::endl;
    }
    System &system = dc.system();
    std::cout << "Waiting for connection: " << std::endl;
    sleep_for(seconds(2));
    std::cout << "End of program" << std::endl;
    auto telemetry = std::make_shared<Telemetry>(system);
    bool a = telemetry->health_all_ok();
    std::cout << "Is health good?" << a << std::endl;

}
