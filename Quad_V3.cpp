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

bool flag = false; // To check if the thread is killed or not. 
bool is_done = false;
std::mutex is_done_mutex;

struct Rates {
	float roll;
	float pitch;
	float yaw;
	float thrust;
};

class Saftey_Net
{
public:
	float min_x = -3.0f;
	float max_x = 3.0f;
	float min_y = -3.0f;
	float max_y = 3.0f;
	float min_z = -3.0f;
	float max_z = 3.0f;
	float max_x_angle = 3.0f;
	float max_y_angle = 3.0f;
	float max_z_angle = 3.0f;
	float max_x_vel = 3.0f;
	float max_y_vel = 3.0f;
	float max_z_vel = 3.0f;

	void set_sn_dimension(float x_min, float x_max, float y_min, float y_max, float z_min, float z_max)
	{
		min_x = x_min;
		max_x = x_max;
		min_y = y_min;
		max_y = y_max;
		min_z = z_min;
		max_z = z_max;
	}

	void set_sn_angles(float x_max_angle, float y_max_angle, float z_max_angle)
	{
		if (x_max_angle > 180.0f || y_max_angle > 180.0f || z_max_angle > 180f)
		{
			max_x_angle = x_max_angle / 2;
			max_y_angle = y_max_angle / 2;
			max_z_angle = z_max_angle / 2;
		}
		else
		{
			max_x_angle = x_max_angle;
			max_y_angle = y_max_angle;
			max_z_angle = z_max_angle;
		}
	}
	void set_sn_velocity(float x_max_vel, float y_max_vel, float z_max_vel)
	{
		max_x_vel = x_max_vel;
		max_y_vel = y_max_vel;
		max_z_vel = z_max_vel;
	}
};

using namespace dronecode_sdk;
Rates close_loop(float, float, float, std::shared_ptr<Telemetry> telemetry);

void user_tests(std::shared_ptr<Telemetry> telemetry, std::shared_ptr<Offboard> offboard, std::shared_ptr<Action> action, std::future<void> futureObj)
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
	offboard->set_attitude_rate({ 0.0f, 0.0f, -60.0f, 0.5f });
	while (futureObj.wait_for(std::chrono::milliseconds(1)) == std::future_status::timeout)
	{
		std::cout << "Called by the user thread." << std::endl;
		for (int i = 0; i < 1000; i++)
		{
			if (telemetry->attitude_euler_angle().yaw_deg <= 45.0f)
			{
				auto roll_deg = close_loop(-60.0f, 0.0f, 0.0f, telemetry);
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

		// Task completed.
		is_done = true;
	}
}

TEST_F(SitlTest, OffboardUserDefined)
{
	DronecodeSDK dc;
	Safety_Net sn;

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

	// health_all_ok() will always return false on the actual Quad without GPS. // 
	while (!telemetry->health_all_ok())
	{
		std::cout << "waiting for system to be ready" << std::endl;
		std::this_thread::sleep_for(std::chrono::seconds(1));
	}

	//Start user thread!
	std::thread user_thread(&user_tests, telemetry, offboard, action, std::move(futureObj)); // Pass list of objects. 

	//Waiting for 2 seconds
	std::this_thread::sleep_for(std::chrono::seconds(2));

	//Safety net checks:
	while (true)
	{
		std::this_thread::sleep_for(std::chrono::milliseconds(5));

		Telemetry::PositionVelocityNED pos = telemetry->position_velocity_ned();
		Telemetry::EulerAngle d_angle = telemetry->attitude_euler_angle();

		//Checks Virtual Box:
		if (abs(pos.position.north_m) > abs(sn.min_x) || abs(pos.position.north_m) > sn.max_x || abs(pos.position.east_m) > abs(sn.min_y) || pos.position.east_m > sn.max_y || abs(pos.position.down) > abs(sn.min_z) || pos.position.down > sn.max_z)
		{
			flag = true;
			std::cout << "Quad Out of safety net" << "North: " << pos.position.north_m << "East: " << pos.position.east_m << "Down: " << abs(pos.position.down_m) << std::endl;
			break;
		}

		//Checking Angle:
		else if (abs(d_angle.roll_deg) > abs(sn.min_roll_angle) || abs(d_angle.pitch_deg) > sn.max_roll_angle || abs(d_angle.yaw_deg) > sn.max_yaw_angle)
		{

			flag = true;
			std::cout << "Quad exceeded safe angular rates" << " Roll: " << angle.roll_deg << " Pitch: " << angle.pitch_deg << " Yaw: " << angle.yaw_deg) << std::endl;
			break;
		}

		//Checking velocity: 
		else if (pos.position.north_m_s > sn.max_x || pos.velocity.east_m_s > sn.max_y_vel || pos.velocity.down_m_s > sn.max_z_vel)
		{
			flag = true;
			std::cout << "Quad exceeded safe velocity" << " North in m/s: " << pos.velocity.north_m_s << " East in m/s: " << pos.velocity.east_m_s << " Down in m/s: " << pos.velocity.down_m_s << std::endl;
			break;
		}

		std::lock_guard<std::mutex> lock(is_done_mutex);
		else if (is_done == true)
		{
			std::cout << "User Script is done" << std::endl;
		}
	}

	if (flag == true)
	{
		exitSignal.set_value();
		flag = true;
		std::this_thread::sleep_for(std::chrono::milliseconds(10));
	}
	action->land();
	std::this_thread::sleep_for(std::chrono::seconds(1));
	action->disarm();
}

//Creating a closing function:
Rates close_loop(float roll_rate, float pitch_rate, float yaw_rate, std::shared_ptr<Telemetry> telemetry)
{
	double roll_control = 6.0 * (double)(roll_rate - telemetry->attitude_euler_angle().roll_deg);
	double pitch_control = 7.2 * (double)(pitch_rate - telemetry->attitude_euler_angle().pitch_deg);
	double yaw_control = 3.80 * (double)(yaw_rate - telemetry->attitude_euler_angle().yaw_deg);
	double thrust_control = 0.1 * (double)(10.5f - telemetry->position().relative_altitude_m);
	if (thrust_control < 0.1)
	{
		thrust_control = 0.35;
	}
	return { (float)roll_control, (float)pitch_control, (float)yaw_control, (float)(thrust_control) };
}
