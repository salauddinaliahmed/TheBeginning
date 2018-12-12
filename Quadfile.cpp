#include <iostream>
#include <cmath>
#include <thread>
#include "integration_test_helper.h"
#include "dronecode_sdk.h"
#include "plugins/action/action.h"
#include "plugins/telemetry/telemetry.h"
#include "plugins/offboard/offboard.h"
#include <future>
#include <assert.h>

public volatile bool flag = True; // To check if the thread is killed or not. 
std::mutex bool is_done;
public float sn_x_distance = 1; // Set to 1 meter each as default.
public float sn_y_distance = 1;
public float sn_z_distance = 1;

struct Rates {
	float roll;
	float pitch;
	float yaw;
	float thrust;
};
using namespace dronecode_sdk;
Rates close_loop(float, float, float, std::shared_ptr<Telemetry> telemetry);

TEST_F(SitlTest, OffboardUserDefined)
{
	DronecodeSDK dc;
	ConnectionResult ret = dc.add_udp_connection("udp://:14540"); //For connecting with Jmavsim simulator.
	ASSERT_EQ(ConnectionResult::SUCCESS, ret);
	std::promise<void> exitSignal;
	std::future<void> futureObj = exitSignal.get_future();

	// Wait for system to connect via heartbeat.
	std::this_thread::sleep_for(std::chrono::seconds(2));
	System &system = dc.system();
	auto telemetry = std::make_shared<Telemetry>(system);
	auto action = std::make_shared<Action>(system);
	auto offboard = std::make_shared<Offboard>(system);

	// health_all_ok() will always return false on the actual Quad without GPS. // Can be changed to a position check too. ( Receiving position or not)
	while (!telemetry->health_all_ok()) {
		std::cout << "waiting for system to be ready" << std::endl;
		std::this_thread::sleep_for(std::chrono::seconds(1));
	}

	//Start user thread!
	std::thread user_thread() // Pass list of objects. 

	//Safety cage conditions. 
	while (true)
	{
		Telemetry::PositionVelocity NED pos = telemetry->position_velocity_ned()
			if (pos.position.north_m < 0 || pos.position.east_m < 0 || pos.position.down_m < 0)
			{
				if (pos.position.north_m < -(sn_x_distance) || pos.position.east_m < -(sn_y_distance) || abs(pos.position.down) < 0.2 || angles > 60 degrees)
				{
					if (flag == false)
					{
						exitSignal.set_value();
						flag = true;
					}
					std::this_thread::sleep_for(std::chrono::milliseconds(10));
					action->set_flight_mode(SystemImpl::FlightMode::HOLD);
				}
			}
			else if (pos.position.north_m > 1 || pos.position.east_m > 1)
			{
				if (flag == false)
				{
					exitSignal.set_value();
					flag = true;
				}
				std::this_thread::sleep_for(std::chrono::milliseconds(10));
				action->set_flight_mode(SystemImpl::FlightMode::HOLD);
			}
		if (is_done == true)
		{
			break;
		}


	action->land();
	std::this_thread::sleep_for(std::chrono::seconds(1));
	action->disarm();
    							
	}
	

// User method. 
bool user_tests(std::shared_ptr<Telemetry> telemetry, std::shared_ptr<Offboard> offboard, std::shared_ptr<Action> action, std::future<void> futureObj)
{
	Action::Result action_ret = action->arm();
	ASSERT_EQ(Action::Result::SUCCESS, action_ret);

	action_ret = action->takeoff();
	ASSERT_EQ(Action::Result::SUCCESS, action_ret);

	// Taking off and reaching an altitude of 2.5mts
	std::this_thread::sleep_for(std::chrono::seconds(3));

	// Send it once before starting offboard, otherwise it will be rejected.
	offboard->set_attitude_rate({ 0.0f, 0.0f, 0.0f, 0.0f });
	// Printing Pitch, roll and yaw euler angles.
	std::cout << "Roll: " << telemetry->attitude_euler_angle().roll_deg << " Pitch: " << telemetry->attitude_euler_angle().pitch_deg << " Yaw: " << telemetry->attitude_euler_angle().yaw_deg << std::endl;

	//Starting Offboard Mode
	Offboard::Result offboard_result = offboard->start();
	EXPECT_EQ(offboard_result, Offboard::Result::SUCCESS);

	// Gaining altitude
	offboard->set_attitude_rate({ 0.0f, 0.0f, 0.0f, 0.5f });
	std::this_thread::sleep_for(std::chrono::seconds(2));

	//Performing Acutal tests
	//Testing Roll
	std::cout << "Rolling at 45 degrees/seconds" << std::endl;
	offboard->set_attitude_rate({ 45.0f, 0.0f, 0.0f, 0.5f });
	while (futureObj.wait_for(std::chrono::milliseconds(1)) == std:future_status::timeout)
	{
		for (int i = 0; i < 1000; i++)
		{
			if (telemetry->attitude_euler_angle().roll_deg <= 45.0f)
			{
				auto roll_deg = close_loop(45.0f, 0.0f, 0.0f, telemetry);
				offboard->set_attitude_rate({ roll_deg.roll, roll_deg.pitch, roll_deg.yaw, roll_deg.thrust });
				std::this_thread::sleep_for(std::chrono::milliseconds(10));
			}
			else
			{
				std::cout << "Roll Angle Reached" << std::endl;
				std::cout << "Roll: " << telemetry->attitude_euler_angle().roll_deg << " Pitch: " << telemetry->attitude_euler_angle().pitch_deg << " Yaw: " << telemetry->attitude_euler_angle().yaw_deg << std::endl;
				break;
			}
		}

		// Balancing
		for (int i = 0; i < 1000; i++)
		{
			if (telemetry->attitude_euler_angle().roll_deg >= 0.2f)
			{
				auto roll_bal = close_loop(0.0f, 0.0f, 0.0f, telemetry);
				offboard->set_attitude_rate({ roll_bal.roll, roll_bal.pitch, roll_bal.yaw, roll_bal.thrust });
				std::this_thread::sleep_for(std::chrono::milliseconds(10));
			}
			else
			{
				std::cout << "Balancing Roll" << std::endl;
				std::cout << "Roll: " << telemetry->attitude_euler_angle().roll_deg << " Pitch: " << telemetry->attitude_euler_angle().pitch_deg << " Yaw: " << telemetry->attitude_euler_angle().yaw_deg << std::endl;
				break;
			}
		}

		is_done = true;
	}
}
