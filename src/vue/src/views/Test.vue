<template>
    <div>
        done
    </div>
</template>

<script>
import auth from '@/api/auth'

function testCourses () {
    auth.get('courses')
        .then(resp => {
            if (!resp || resp.length < 4) {
                console.log('get /courses/ does not work')
                console.log(resp)
            }
        })
        .catch(resp => console.log(resp))
    auth.get('courses/1')
        .then(resp => {
            if (!resp || resp.name !== 'Is PAV') {
                console.log('get /courses/1 does not work')
                console.log(resp)
            }
        })
        .catch(resp => console.log(resp))
    auth.create('courses', {name: 'test', abbr: 'te'})
        .then(resp => {
            if (!resp || resp.description !== 'Succesfully created course.') {
                console.log('create /courses/ does not work')
                console.log(resp)
            }
        })
        .catch(resp => console.log(resp))
    auth.update('courses/1', {name: 'Is PAV'})
        .then(resp => {
            if (!resp || resp.result.name !== 'Is PAV') {
                console.log('update /courses/1 does not work')
                console.log(resp)
            }
        })
        .catch(resp => console.log(resp))
    auth.get('courses/1/users')
        .then(resp => {
            if (!resp || resp.length < 4) {
                console.log('get /courses/users does not work')
                console.log(resp)
            }
        })
        .catch(resp => console.log(resp))

    auth.update('courses/1', {lti_id: '5'})
        .then(resp => {
            if (!resp || resp.result.lti_id !== '5') {
                console.log('update lti /courses/1 does not work')
                console.log(resp)
            }
        })
}

function testRoles () {
    var name = 'ProStudent' + Math.random()
    auth.get('courses/1/roles')
        .then(resp => {
            if (!resp || resp.length <= 3) {
                console.log('get /courses/1/roles does not work')
                console.log(resp)
            }
        })
    auth.update('courses/1/roles', {roles: [{
        name: 'Student', can_edit_course_details: false
    }]})
        .then(resp => {
            resp = resp.result
            if (!resp || resp.length !== 1 || resp[0].can_edit_course_details !== false) {
                console.log('patch /courses/1/roles does not work')
                console.log(resp)
            }
        })
    auth.update('courses/1/roles', {roles: [{
        name: 'Student', can_edit_course_details: true
    }]})
        .then(resp => {
            resp = resp.result
            if (!resp || resp.length !== 1 || resp[0].can_edit_course_details !== true) {
                console.log('patch /courses/1/roles does not work')
                console.log(resp)
            }
        })
    auth.create('courses/1/roles', {
        name: name,
        permissions: {can_edit_course_details: true}
    })
        .then(resp => {
            resp = resp.result
            if (!resp || resp[0].can_edit_course_details !== true) {
                console.log('create /courses/1/roles does not work')
                console.log(resp)
            }
        })
    auth.delete('courses/1/roles', {name: name})
        .then(resp => {
            console.log(resp)
            if (!resp || resp.description !== 'Succesfully deleted course.') {
                console.log('destroy /courses/1/roles does not work')
                console.log(resp)
            }
        })
}

function testUsers () {
    var name = 'test' + Math.random()
    auth.get('users')
        .then(resp => {
            if (!resp || resp.length <= 3) {
                console.log('get /users/ does not work')
                console.log(resp)
            }
        })
    auth.get('users/1')
        .then(resp => {
            if (!resp || resp.first_name !== 'Lars') {
                console.log('get /users/1 does not work')
                console.log(resp)
            }
        })
    auth.get('users/6')
        .then(resp => {
            if (!resp || resp.id !== 6 || !resp.grade_notifications) {
                console.log('get /users/6 does not work (logged in user)')
                console.log(resp)
            }
        })
    auth.create('users', {username: name, password: 'Test123!'})
        .then(resp => {
            if (!resp || resp.description !== 'Succesfully created user.') {
                console.log('create /users/ does not work')
                console.log(resp)
            }
        })
        .catch(resp => console.log(resp))
}

function testAssignments () {
    auth.create('assignments', {name: 'test', description: 'test descrip', cID: '1', points_possible: '1'})
        .then(resp => {
            if (!resp || resp.description !== 'Succesfully created assignment.') {
                console.log('create /assignments/ does not work')
                console.log(resp)
            }
        })
        .catch(resp => console.log(resp))
    auth.get('assignments/1')
        .then(resp => {
            if (!resp || resp.name !== 'Logboek') {
                console.log('get /assignments/1 does not work')
                console.log(resp)
            }
        })
        .catch(resp => console.log(resp))
    auth.update('assignments/1', {name: 'Logboek test'})
        .then(resp => {
            if (!resp || resp.result.name !== 'Logboek test') {
                console.log('update /assignments/1 does not work')
                console.log(resp)
            }
        })
    auth.update('assignments/1', {name: 'Logboek'})
        .then(resp => {
            if (!resp || resp.result.name !== 'Logboek') {
                console.log('update /assignments/1 does not work')
                console.log(resp)
            }
        })
}

export default {
    created () {
        auth.login('Teacher', 'pass')
            .then(_ => {
                testCourses()
            })
            .catch(err => console.log(err))
    },

    dontRun () {
        testAssignments()
        testRoles()
        testUsers()
    }
}
</script>
