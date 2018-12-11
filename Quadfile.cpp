#include <iostream>
#include <cmath>
#include "integration_test_helper.h"
#include "dronecode_sdk.h"
#include "plugins/action/action.h"
#include "plugins/telemetry/telemetry.h"
#include "plugins/offboard/offboard.h"

using namespace dronecode_sdk;
struct Rates {
    float roll;
    float pitch;
    float yaw;
    float thrust;
};
Rates close_loop(float, float, float, std::shared_ptr<Telemetry> telemetry);


TEST_F(SitlTest, OffboardAttitudeRate)
{
    DronecodeSDK dc;

    ConnectionResult ret = dc.add_udp_connection("udp://:14540"); //For connecting with Jmavsim simulator.
    ASSERT_EQ(ConnectionResult::SUCCESS, ret);

    // Wait for system to connect via heartbeat.
    std::this_thread::sleep_for(std::chrono::seconds(2));

    System &system = dc.system();
    auto telemetry = std::make_shared<Telemetry>(system);
    auto action = std::make_shared<Action>(system);
    auto offboard = std::make_shared<Offboard>(system);

    while (!telemetry->health_all_ok()) {
        std::cout << "waiting for system to be ready" << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    Action::Result action_ret = action->arm();
    ASSERT_EQ(Action::Result::SUCCESS, action_ret);

    action_ret = action->takeoff();
    ASSERT_EQ(Action::Result::SUCCESS, action_ret);

    // Taking off and reaching an altitude of 2.5mts
    std::this_thread::sleep_for(std::chrono::seconds(3));

    // Send it once before starting offboard, otherwise it will be rejected.
    offboard->set_attitude_rate({0.0f, 0.0f, 0.0f, 0.0f});
    // Printing Pitch, roll and yaw euler angles.
    std::cout<< "Roll: "<<telemetry->attitude_euler_angle().roll_deg << " Pitch: " <<telemetry->attitude_euler_angle().pitch_deg << " Yaw: " << telemetry->attitude_euler_angle().yaw_deg << std::endl;

    //Starting Offboard Mode
    Offboard::Result offboard_result = offboard->start();
    EXPECT_EQ(offboard_result, Offboard::Result::SUCCESS);

    // Gaining altitude
    offboard->set_attitude_rate({0.0f, 0.0f, 0.0f, 0.6f});
    std::this_thread::sleep_for(std::chrono::seconds(2));

    //Performing Acutal tests
    //Testing Roll
    std::cout << "Rolling at 45 degrees/seconds" << std::endl;
    offboard->set_attitude_rate({45.0f, 0.0f, 0.0f, 0.6f});
    for (int i=0; i<1000; i++)
    {
        if (telemetry->attitude_euler_angle().roll_deg <= 45.0f)
        {
            auto c1 = close_loop(45.0f,0.0f,0.0f,telemetry);
            offboard->set_attitude_rate({c1.roll, c1.pitch, c1.yaw, c1.thrust});
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        else
        {
            std::cout<< "Roll: "<<telemetry->attitude_euler_angle().roll_deg << " Pitch: " <<telemetry->attitude_euler_angle().pitch_deg << " Yaw: " << telemetry->attitude_euler_angle().yaw_deg << std::endl;
            break;
        }
     }
     std::cout<< "Pitch: "<<telemetry->attitude_euler_angle().pitch_deg << " Roll: " << telemetry->attitude_euler_angle().roll_deg << " Yaw: " << telemetry->attitude_euler_angle().yaw_deg << std::endl;

    // Balancing
    for (int i=0; i<1000; i++)
    {
         if (telemetry->attitude_euler_angle().roll_deg >= 0.02f)
         {
             auto c = close_loop(0.0f,0.0f,0.0f,telemetry);
             offboard->set_attitude_rate({c.roll, c.pitch, c.yaw, c.thrust});
             std::this_thread::sleep_for(std::chrono::milliseconds(10));
             std::cout << c.thrust << std::endl;
         }
         else
         {
             std::cout<< "Roll: "<<telemetry->attitude_euler_angle().roll_deg << " Pitch: " <<telemetry->attitude_euler_angle().pitch_deg << " Yaw: " << telemetry->attitude_euler_angle().yaw_deg << std::endl;
             break;
         }
    }

    std::this_thread::sleep_for(std::chrono::seconds(5));

    offboard_result = offboard->stop();
    EXPECT_EQ(offboard_result, Offboard::Result::SUCCESS);
    action_ret = action->land();
    std::cout << "Landed! " << std::endl;

    std::this_thread::sleep_for(std::chrono::seconds(3));
    std::cout<< "Pitch: "<<telemetry->attitude_euler_angle().pitch_deg << " Roll: " <<telemetry->attitude_euler_angle().roll_deg << " Yaw: " << telemetry->attitude_euler_angle().yaw_deg << std::endl;
    EXPECT_EQ(action_ret, Action::Result::SUCCESS);
}
//Creating a function:

Rates close_loop(float roll_rate, float pitch_rate, float yaw_rate, std::shared_ptr<Telemetry> telemetry)
{
    double roll_control = 6.0 * (double) (roll_rate - telemetry->attitude_euler_angle().roll_deg);
    double pitch_control = 6.0 * (double) (pitch_rate - telemetry->attitude_euler_angle().pitch_deg);
    double yaw_control = 2.80 * (double) (yaw_rate - telemetry->attitude_euler_angle().yaw_deg);
    double thrust_control = 0.75 * (double) (10.5f -  telemetry->position().relative_altitude_m);
    std::cout << roll_control << "::" << pitch_control << "::" << yaw_control <<":T:" << thrust_control << std::endl ;
    return {(float) roll_control, (float) pitch_control, (float) yaw_control, (float) thrust_control};
}

