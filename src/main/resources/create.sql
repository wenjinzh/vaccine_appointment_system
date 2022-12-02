CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients(
	Username varchar(255),
	Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Appointments(
	Appointment_id int identity(1,1),
	Time date,
	cname varchar(255) REFERENCES Caregivers(Username),
	vname varchar(255) REFERENCES Vaccines(Name),
	pname varchar(255) REFERENCES Patients(Username),
	PRIMARY KEY(Appointment_id)
);