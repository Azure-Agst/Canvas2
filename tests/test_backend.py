import pytest
from bson import ObjectId
from datetime import datetime, timedelta

from .utils import setuser, setbogus

###############################################################################
#  CLASS CREATION TESTS
###############################################################################


def test_addcourse_good(client):
    """Tests adding a course to the database."""

    # set teacher
    user = setuser(client, "teacher")

    # use client context
    with client:

        # try making course
        res = client.post(
            "/secretary/add-course",
            data={
                "course-name": "PyTest Course 1",
                "course-code": "PYT001",
                "course-desc": "This course was made by PyTest! "
                + "(test_addcourse_good)",
            },
            follow_redirects=True,
        )

        # check to make sure we were redirected to new class page
        assert res.status_code == 200
        assert "/c/" in res.request.path

        # assert class was actually created in db
        course = pytest.db["classes"].find_one({"code": "PYT001"})
        assert course is not None

        # assert teacher was added to class
        enrollment = pytest.db["enrollments"].find_one(
            {"class": course["_id"], "user": user["_id"]}
        )
        assert enrollment is not None


def test_addcourse_noauth(client):
    """Tests adding a course to the database while a user is not logged in."""

    # use client context
    with client:

        # try making course
        res = client.post(
            "/secretary/add-course",
            data={
                "course-name": "PyTest Course 2",
                "course-code": "PYT002",
                "course-desc": "This course should never be made by PyTest! "
                + "(test_addcourse_noauth)",
            },
            follow_redirects=True,
        )

        # check to make sure we were unauthorized
        assert res.status_code == 401

        # assert class was not created in db
        course = pytest.db["classes"].find_one({"code": "PYT002"})
        assert course is None


def test_addcourse_noperms(client):
    """Tests adding a course to the database while a user doesnt have perms."""

    # set student
    setuser(client, "student1")

    # use client context
    with client:

        # try logging in with user credentials
        res = client.post(
            "/secretary/add-course",
            data={
                "course-name": "PyTest Course 3",
                "course-code": "PYT003",
                "course-desc": "This course should never be made by PyTest! "
                + " (test_addcourse_noperms)",
            },
            follow_redirects=True,
        )

        # check to make sure we were forbidden
        assert res.status_code == 403

        # assert class was not created in db
        course = pytest.db["classes"].find_one({"code": "PYT003"})
        assert course is None


###############################################################################
#  ASSIGNMENT CREATION TESTS
###############################################################################


def test_createassg_good(client):
    """Tests adding an assignment to a class"""

    # set teacher
    setuser(client, "teacher")

    # get class id from db
    course = pytest.db["classes"].find_one({"title": "Test Course 2"})

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/create-assg",
            data={
                "assg-name": "Calculus Homework 1",
                "assg-desc": "Page 32 of the textbook, #6-12",
                "course-code": str(course["_id"]),
                "due-date": (datetime.now() + timedelta(days=1)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
            headers={"Referer": "/c/" + str(course["_id"])},
            follow_redirects=True,
        )

        # check to make sure we were permitted
        assert res.status_code == 200

        # ensure assignment was made
        assignment = pytest.db["assignments"].find_one(
            {"title": "Calculus Homework 1"}
        )
        assert assignment is not None


def test_createassg_noauth(client):
    """Tests adding an assignment to a class without being logged in."""

    # get class id from db
    course = pytest.db["classes"].find_one({"title": "Test Course 2"})

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/create-assg",
            data={
                "assg-name": "Calculus Homework 2",
                "assg-desc": "Page 64 of the textbook, #12-24",
                "course-code": str(course["_id"]),
                "due-date": (datetime.now() + timedelta(days=1)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
            headers={"Referer": "/c/" + str(course["_id"])},
            follow_redirects=True,
        )

        # check to make sure we were unauthorized
        assert res.status_code == 401

        # ensure assignment was not made
        assignment = pytest.db["assignments"].find_one(
            {"title": "Calculus Homework 2"}
        )
        assert assignment is None


def test_createassg_nouser(client):
    """Tests adding an assignment using spoofed session data that doesnt
    exist."""

    # set bogus user
    setbogus(client)

    # get class id from db
    course = pytest.db["classes"].find_one({"title": "Test Course 2"})

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/create-assg",
            data={
                "assg-name": "Calculus Homework 3",
                "assg-desc": "Page 128 of the textbook, #24-48",
                "course-code": str(course["_id"]),
                "due-date": (datetime.now() + timedelta(days=1)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
            headers={"Referer": "/c/" + str(course["_id"])},
            follow_redirects=True,
        )

        # check to make sure we were forbidden
        assert res.status_code == 403

        # ensure assignment was not made
        assignment = pytest.db["assignments"].find_one(
            {"title": "Calculus Homework 3"}
        )
        assert assignment is None


def test_createassg_noperms(client):
    """Tests adding an assignment using student data, which shouldn't be
    allowed."""

    # set student
    setuser(client, "student1")

    # get class id from db
    course = pytest.db["classes"].find_one({"title": "Test Course 2"})

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/create-assg",
            data={
                "assg-name": "Calculus Homework 4",
                "assg-desc": "Page 256 of the textbook, #48-96",
                "course-code": str(course["_id"]),
                "due-date": (datetime.now() + timedelta(days=1)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
            headers={"Referer": "/c/" + str(course["_id"])},
            follow_redirects=True,
        )

        # check to make sure we were forbidden
        assert res.status_code == 403

        # ensure assignment was not made
        assignment = pytest.db["assignments"].find_one(
            {"title": "Calculus Homework 4"}
        )
        assert assignment is None


def test_createassg_noenroll(client):
    """Tests adding an assignment to a class we're not allowed to
    administer."""

    # set teacher
    setuser(client, "teacher")

    # get class id from db
    course = pytest.db["classes"].find_one({"title": "Hidden Course"})

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/create-assg",
            data={
                "assg-name": "Calculus Homework 5",
                "assg-desc": "Page 512 of the textbook, #96-192",
                "course-code": str(course["_id"]),
                "due-date": (datetime.now() + timedelta(days=1)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
            headers={"Referer": "/c/" + str(course["_id"])},
            follow_redirects=True,
        )

        # check to make sure we were forbidden
        assert res.status_code == 403

        # ensure assignment was not made
        assignment = pytest.db["assignments"].find_one(
            {"title": "Calculus Homework 5"}
        )
        assert assignment is None


###############################################################################
#  ASSIGNMENT SUBMISSION TESTS
###############################################################################


def test_submitassg_good(client):
    """Tests Student1 submitting to Assignment 2"""

    # set student
    user = setuser(client, "student1")

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 2"}
    )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_good)",
                "assg-course": assignment["class"],
                "assg-user-id": str(user["_id"]),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were allowed
        assert res.status_code == 200
        assert res.request.path == f"/c/{assignment['class']}"

        # ensure submission was made
        submission = pytest.db["submissions"].find_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )
        assert submission is not None

        # clean up
        pytest.db["submissions"].delete_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )


def test_submitassg_noauth(client):
    """Tests Student1 submitting with no auth"""

    # get student 1 id
    student1_id = pytest.db["users"].find_one(
        {"username": "student1"}
    )["_id"]

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 2"}
    )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_noauth)",
                "assg-course": assignment["class"],
                "assg-user-id": str(student1_id),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were unauthorized
        assert res.status_code == 401

        # ensure submission was not made
        submission = pytest.db["submissions"].find_one(
            {"assignment": assignment["_id"], "user": student1_id}
        )
        assert submission is None

        # clean up
        pytest.db["submissions"].delete_one(
            {"assignment": assignment["_id"], "user": student1_id}
        )


def test_submitassg_nouser(client):
    """Tests submitting with spoofed user data"""

    # set bogus user
    setbogus(client)

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 2"}
    )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_nouser)",
                "assg-course": assignment["class"],
                "assg-user-id": "6245d9258519c7e387c9e85f",
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were given bad request
        assert res.status_code == 400

        # ensure submission was not made
        submission = pytest.db["submissions"].find_one(
            {
                "assignment": assignment["_id"],
                "user": ObjectId("6245d9258519c7e387c9e85f"),  # bogus's user id
            }
        )
        assert submission is None

        # clean up
        pytest.db["submissions"].delete_one(
            {
                "assignment": assignment["_id"],
                "user": ObjectId("6245d9258519c7e387c9e85f"),  # bogus's user id
            }
        )


def test_submitassg_noperms(client):
    """Tests teacher submitting to Assignment 2"""

    # set teacher
    user = setuser(client, "teacher")

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 2"}
    )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_noperms)",
                "assg-course": assignment["class"],
                "assg-user-id": str(user["_id"]),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were forbidden
        assert res.status_code == 403

        # ensure submission was not made
        submission = pytest.db["submissions"].find_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )
        assert submission is None

        # clean up
        pytest.db["submissions"].delete_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )


def test_submitassg_noforgery(client):
    """Tests Student2 submitting to Assignment 2 on Student1's behalf"""

    # set student 2
    setuser(client, "student2")

    # get student 1 id
    student1_id = pytest.db["users"].find_one(
        {"username": "student1"}
    )["_id"]

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 2"}
    )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_nocsrf)",
                "assg-course": assignment["class"],
                "assg-user-id": str(student1_id),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were forbidden
        assert res.status_code == 403

        # ensure submission was not made
        submission = pytest.db["submissions"].find_one(
            {"assignment": assignment["_id"], "user": student1_id}
        )
        assert submission is None

        # clean up
        pytest.db["submissions"].delete_one(
            {"assignment": assignment["_id"], "user": student1_id}
        )


def test_submitassg_noassg(client):
    """Tests Student1 submitting to a bogus assignment"""

    # set student
    user = setuser(client, "student1")

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 2"}
    )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": ObjectId("6245d9258519c7e387c9e85f"),
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_noassg)",
                "assg-course": assignment["class"],
                "assg-user-id": str(user["_id"]),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were denied
        assert res.status_code == 400

        # ensure submission was not made
        submission = pytest.db["submissions"].find_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )
        assert submission is None

        # clean up
        pytest.db["submissions"].delete_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )


def test_submitassg_noenroll(client):
    """Tests Student2 submitting to a class they're not enrolled in"""

    # set student 2
    user = setuser(client, "student2")

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 2"}
    )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_noenroll)",
                "assg-course": assignment["class"],
                "assg-user-id": str(user["_id"]),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were denied
        assert res.status_code == 403

        # ensure submission was not made
        submission = pytest.db["submissions"].find_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )
        assert submission is None

        # clean up
        pytest.db["submissions"].delete_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )

def test_delete_assignment(client):

    # set teach
    user = setuser(client, "teacher")

    # get assignment id from db
    course = pytest.db["classes"].find_one({"code": "TEST002"})
    assg_id = pytest.db["assignments"].insert_one({
        "class": course['_id'],
        "title": "Delete me too!",
        "description": "This is the deleted assignment!",
        "deadline": datetime.now(),
    }).inserted_id

    # use client context
    with client:

        res = client.post(
            "/secretary/delete_assg",
            data={
                "assg-id": str(assg_id),
                "crs-code": str(course["_id"])
            },
            headers={"Referer": "/c/" + str(course['_id'])},
            follow_redirects=True,
        )

        # check to make sure we were allowed
        assert res.status_code == 200

        # ensure assignment was deleted
        assignment = pytest.db["assignments"].find_one({
            "_id": assg_id
        })
        assert assignment is None


def test_delete_submission(client):

    # set teach
    setuser(client, "teacher")

    # get assignment id from db
    assg = pytest.db["assignments"].find_one({"title": "Test Assignment 2"})
    sub_id = pytest.db["assignments"].insert_one({
        "class": assg['_id'],
        "title": "Delete me too!",
        "description": "This is the deleted submission!",
    }).inserted_id  # literally whatever

    # use client context
    with client:

        res = client.post(
            "/secretary/delete_sub",
            data={
                "sub-id": str(sub_id),
            },
            headers={"Referer": "/c/" + str(assg['class'])},
            follow_redirects=True,
        )

        # check to make sure we were allowed
        assert res.status_code == 200

        # ensure assignment was deleted
        assignment = pytest.db["submissions"].find_one({
            "_id": sub_id
        })
        assert assignment is None