<template>
    <content-single-column>
        <h1 class="mb-2">{{ currentPage }}</h1>
        <b-card class="no-hover blue-border">
            <lti-create-link-course v-if="handleCourseChoice" @handleAction="handleActions" :lti="lti" :courses="courses"/>
            <lti-create-link-assignment v-else-if="handleAssignmentChoice" @handleAction="handleActions" :lti="lti" :page="page"/>
            <div v-else class="center-content">
                <h2 class="center-content">Setting up a link to your learning environment</h2><br/>
                <icon name="circle-o-notch" pulse scale="1.5"/>
            </div>
        </b-card>
    </content-single-column>
</template>

<script>
import contentSingleColumn from '@/components/columns/ContentSingleColumn.vue'
import ltiCreateLinkCourse from '@/components/lti/LtiCreateLinkCourse.vue'
import ltiCreateLinkAssignment from '@/components/lti/LtiCreateLinkAssignment.vue'
import ltiAPI from '@/api/lti'
import router from '@/router'
import courseAPI from '@/api/course.js'
import assignmentAPI from '@/api/assignment.js'
import genericUtils from '@/utils/generic_utils.js'
import icon from 'vue-awesome/components/Icon'

export default {
    name: 'LtiLaunch',
    components: {
        'content-single-column': contentSingleColumn,
        'lti-create-link-course': ltiCreateLinkCourse,
        'lti-create-link-assignment': ltiCreateLinkAssignment,
        icon
    },
    data () {
        return {
            currentPage: 'LTI Integration',

            /* Variables for loading the right component. */
            handleCourseChoice: false,
            handleAssignmentChoice: false,
            ltiJWT: '',
            tempStateToCheckIfWeCanAutoSetup: '',

            /* Possible states for the control flow. */
            states: {
                state: '',

                /* Extern variables for checking the state of the lti launch. */
                bad_auth: '-1',
                no_course: '0',
                no_assign: '1',
                new_course: '2',
                new_assign: '3',
                finish_t: '4',
                finish_s: '5',
                grade_center: '6',

                /* Intern variables for checking the state of the lti launch. */
                check_assign: '7'
            },

            /* Set a dictionary with the needed lti variables. */
            lti: {
                ltiCourseID: '',
                ltiCourseName: '',
                ltiCourseAbbr: '',
                ltiCourseStart: '',
                ltiAssignName: '',
                ltiAssignID: '',
                ltiAssignPublished: '',
                ltiPointsPossible: '',
                ltiAssignUnlock: '',
                ltiAssignDue: '',
                ltiAssignLock: ''
            },

            /* Set a dictionary with the variables of the linked page. */
            page: {
                cID: '',
                aID: '',
                jID: ''
            },

            courses: null
        }
    },
    methods: {
        loadLtiData () {
            return ltiAPI.getLtiParams(this.ltiJWT)
                .then(response => {
                    this.lti.ltiCourseName = response.lti_cName
                    this.lti.ltiCourseAbbr = response.lti_abbr
                    this.lti.ltiCourseID = response.lti_cID
                    this.lti.ltiCourseStart = response.lti_course_start
                    this.lti.ltiAssignName = response.lti_aName
                    this.lti.ltiAssignID = response.lti_aID
                    this.lti.ltiPointsPossible = response.lti_points_possible
                    this.lti.ltiAssignUnlock = response.lti_aUnlock
                    this.lti.ltiAssignDue = response.lti_aDue
                    this.lti.ltiAssignLock = response.lti_aLock
                    this.lti.ltiAssignPublished = response.lti_aPublished
                    this.page.cID = response.cID
                    this.page.aID = response.aID
                    this.page.jID = response.jID
                    this.tempStateToCheckIfWeCanAutoSetup = response.state
                })
        },
        autoSetupCourseAndAssignment () {
            courseAPI.create({
                name: this.lti.ltiCourseName,
                abbreviation: this.lti.ltiCourseAbbr,
                startdate: this.lti.ltiCourseStart.split(' ')[0],
                enddate: genericUtils.yearOffset(this.lti.ltiCourseStart.split(' ')[0]),
                lti_id: this.lti.ltiCourseID }).then(course => {
                this.page.cID = course.id
                assignmentAPI.create({
                    name: this.lti.ltiAssignName,
                    description: 'No content.',
                    course_id: this.page.cID,
                    lti_id: this.lti.ltiAssignID,
                    points_possible: this.lti.ltiPointsPossible,
                    unlock_date: this.lti.ltiAssignUnlock.slice(0, -9),
                    due_date: this.lti.ltiAssignDue.slice(0, -9),
                    lock_date: this.lti.ltiAssignLock.slice(0, -9)
                }).then(assignment => {
                    this.page.aID = assignment.id
                    this.updateState(this.states.finish_t)
                })
            })
        },
        handleActions (args) {
            switch (args[0]) {
            case 'courseCreated':
                this.handleCourseChoice = false
                this.page.cID = args[1]
                this.$toasted.success('Course Created!')
                this.states.state = this.states.check_assign
                break
            case 'courseLinked':
                this.handleCourseChoice = false
                this.page.cID = args[1]
                this.$toasted.success('Course Linked!')
                this.states.state = this.states.check_assign
                break
            case 'assignmentIntegrated':
                this.handleAssignmentChoice = false
                this.page.aID = args[1]
                this.$toasted.success('Assignment Integrated!')
                this.states.state = this.states.finish_t
                break
            case 'assignmentCreated':
                this.page.aID = args[1]
                this.$toasted.success('Assignment Created!')
                this.states.state = this.states.finish_t
                break
            }
        },
        updateState (state) {
            switch (state) {
            case this.states.new_course:
                this.currentPage = 'Course Integration'
                this.handleCourseChoice = true
                break
            case this.states.new_assign:
                this.currentPage = 'Assignment Integration'
                this.handleAssignmentChoice = true
                break
            case this.states.check_assign:
                assignmentAPI.getWithLti(this.lti.ltiAssignID)
                    .then(assignment => {
                        if (assignment === undefined) {
                            this.states.state = this.states.new_assign
                        } else {
                            this.page.aID = assignment.id
                            this.states.state = this.states.finish_t
                        }
                    })
                    .catch(error => {
                        if (error.response.status === 404) {
                            this.states.state = this.states.new_assign
                        }
                    })
                break
            case this.states.grade_center:
                this.$router.push({
                    name: 'Journal',
                    params: {
                        cID: this.page.cID,
                        aID: this.page.aID,
                        jID: this.page.jID
                    }
                })
                break
            case this.states.finish_s:
                /* Student has created a journal for an existing assignment, we need to update the store. */
                this.$store.dispatch('user/populateStore').then(_ => {
                    this.$router.push({
                        name: 'Journal',
                        params: {
                            cID: this.page.cID,
                            aID: this.page.aID,
                            jID: this.page.jID
                        }
                    })
                }, error => {
                    this.$router.push({
                        name: 'ErrorPage',
                        params: {
                            code: error.response.status,
                            reasonPhrase: error.response.statusText,
                            description: `Unable to acquire the newly created journal data, please try again.`
                        }
                    })
                })
                break
            case this.states.finish_t:
                /* Teacher has created or linked a new course and or assignment, we need to update the store. */
                this.$store.dispatch('user/populateStore').then(_ => {
                    this.$router.push({
                        name: 'FormatEdit',
                        params: {
                            cID: this.page.cID,
                            aID: this.page.aID
                        }
                    })
                }, error => {
                    this.$router.push({
                        name: 'ErrorPage',
                        params: {
                            code: error.response.status,
                            reasonPhrase: error.response.statusText,
                            description: `Unable to acquire the newly created assignment data, please try again.`
                        }
                    })
                })
                break
            }
        },
        handleInitialState () {
            if (this.tempStateToCheckIfWeCanAutoSetup === this.states.bad_auth) {
                router.push({
                    name: 'ErrorPage',
                    params: {
                        code: '511',
                        reasonPhrase: 'Network authorization required',
                        description: `Invalid credentials from the LTI environment.
                                      Please contact the system administrator.`
                    }
                })
            } else if (this.tempStateToCheckIfWeCanAutoSetup === this.states.no_course || this.tempStateToCheckIfWeCanAutoSetup === this.states.no_assign) {
                router.push({
                    name: 'ErrorPage',
                    params: {
                        code: '404',
                        reasonPhrase: 'No course found with given ID',
                        description: `The requested course is not available on
                                      ejournal. Wait for it to become availible or
                                      contact your teacher for more information.`
                    }
                })
            }
        }
    },
    watch: {
        'states.state': function (val) {
            this.updateState(this.states.state)
        }
    },
    mounted () {
        this.ltiJWT = this.$route.query.ltiJWT

        this.loadLtiData().then(_ => {
            this.handleInitialState()
            /* The lti parameters such as course id are not set if we are a student. */
            if (this.lti.ltiCourseID) {
                courseAPI.getLinkable().then(courses => {
                    if (courses.length) {
                        this.courses = courses
                        this.states.state = this.tempStateToCheckIfWeCanAutoSetup
                    } else {
                        this.autoSetupCourseAndAssignment()
                    }
                })
            } else {
                this.states.state = this.tempStateToCheckIfWeCanAutoSetup
            }
        }).catch(error => {
            this.$router.push({
                name: 'ErrorPage',
                params: {
                    code: error.response.status,
                    reasonPhrase: error.response.statusText,
                    description: error.response.data.description
                }
            })
        })
    }
}
</script>
