<!-- TODO: You shouldnt be able to change your own role. -->
<template>
    <content-single-column>
        <bread-crumb>&nbsp;</bread-crumb>
        <b-card class="no-hover settings-card">
            <h2 class="mb-2">Manage course data</h2>

            <b-form @submit.prevent="onSubmit">
                <h2 class="field-heading required">Course name</h2>
                <b-input class="mb-2 mr-sm-2 mb-sm-0 multi-form theme-input"
                    :readonly="!$hasPermission('can_edit_course_details')"
                    v-model="course.name"
                    placeholder="Course name"/>
                <h2 class="field-heading required">Course abbreviation</h2>
                <b-input class="mb-2 mr-sm-2 mb-sm-0 multi-form theme-input"
                    :readonly="!$hasPermission('can_edit_course_details')"
                    v-model="course.abbreviation"
                    maxlength="10"
                    placeholder="Course abbreviation (max 10 characters)"/>
                <b-row>
                    <b-col xs="6">
                        <h2 class="field-heading required">From</h2>
                        <flat-pickr class="multi-form theme-input full-width"
                            :class="{ 'input-disabled': !$hasPermission('can_edit_course_details') }"
                            v-model="course.startdate"/>
                    </b-col>
                    <b-col xs="6">
                        <h2 class="field-heading required">To</h2>
                        <flat-pickr class="multi-form theme-input full-width"
                            :class="{ 'input-disabled': !$hasPermission('can_edit_course_details') }"
                            v-model="course.enddate"/>
                    </b-col>
                </b-row>
                <b-button class="add-button float-right"
                    type="submit"
                    v-if="$hasPermission('can_edit_course_details')">
                    <icon name="save"/>
                    Save
                </b-button>
            </b-form>
        </b-card>

        <b-card class="no-hover">
            <b-row>
                <b-col class="d-flex flex-wrap">
                    <b-button v-if="$hasPermission('can_delete_course')"
                        @click.prevent.stop="deleteCourse()"
                        class="multi-form delete-button flex-grow-1">
                        <icon name="trash"/>
                        Delete Course
                    </b-button>
                    <b-button v-if="$hasPermission('can_edit_course_roles')"
                        @click.prevent.stop="routeToEditCourseRoles"
                        class="multi-form change-button flex-grow-1">
                        <icon name="cog"/>
                        Manage Permissions
                    </b-button>
                    <b-btn v-if="$hasPermission('can_edit_course_details')"
                        class="multi-form change-button flex-grow-1"
                        v-b-modal="'CourseGroupModal'">
                        <icon name="users"/>
                        Manage Groups
                    </b-btn>
                </b-col>
            </b-row>
        </b-card>

        <b-modal id="CourseGroupModal"
                 title="Manage Course Groups"
                 hide-footer>
                 <group-modal v-if="$hasPermission('can_edit_course_details')"
                     :cID="this.cID"
                     :groups="this.groups"
                     @create-group="createGroup"
                     @delete-group="deleteGroup"
                     @update-group="updateGroup">
                 </group-modal>
        </b-modal>

        <div>
            <b-card v-if="$hasPermission('can_add_course_users')" class="no-hover">
                <h2 class="mb-2">Manage course members</h2>
                <div class="d-flex">
                    <input
                        class="theme-input flex-grow-1 no-width multi-form mr-2"
                        type="text"
                        v-model="searchVariable"
                        placeholder="Search..."/>
                    <b-button v-if="viewEnrolled" v-on:click.stop @click="toggleEnroled" class="multi-form">
                        <icon name="users"/>
                        Enrolled
                    </b-button>
                    <b-button v-if="!viewEnrolled" v-on:click.stop @click="toggleEnroled" class="multi-form">
                        <icon name="user-plus"/>
                        Unenrolled
                    </b-button>
                </div>
                <div class="d-flex">
                    <b-form-select class="multi-form mr-2" v-model="selectedSortOption" :select-size="1">
                        <option :value="null">Sort by ...</option>
                        <option value="sortFullName">Sort by name</option>
                        <option value="sortUsername">Sort by username</option>
                    </b-form-select>
                    <b-form-select class="multi-form mr-2" v-model="selectedFilterGroupOption"
                                   :select-size="1">
                        <option :value="null">Filter group by ...</option>
                        <option v-for="group in groups" :key="group.name" :value="group.name">
                            {{ group.name }}
                        </option>
                    </b-form-select>
                    <b-button v-on:click.stop v-if="!order" @click="toggleOrder" class="multi-form">
                        <icon name="long-arrow-down"/>
                        Ascending
                    </b-button>
                    <b-button v-on:click.stop v-if="order" @click="toggleOrder" class="multi-form">
                        <icon name="long-arrow-up"/>
                        Descending
                    </b-button>
                </div>
                <b-col sm="8" class="d-flex flex-wrap">
                </b-col>
            </b-card>

            <course-participant-card v-if="viewEnrolled"
                @delete-participant="deleteParticipantLocally"
                @update-participants="updateParticipants"
                v-for="p in filteredUsers"
                :key="p.id"
                :cID="cID"
                :group.sync="p.group"
                :groups="groups"
                :user="p"
                :numTeachers="numTeachers"
                :roles="roles"/>

            <add-user-card v-if="!viewEnrolled"
                @add-participant="addParticipantLocally"
                v-for="p in filteredUsers"
                :key="p.id"
                :cID="cID"
                :user="p"/>
        </div>
    </content-single-column>
</template>

<script>
import addUsersToCourseCard from '@/components/course/AddUsersToCourseCard.vue'
import breadCrumb from '@/components/assets/BreadCrumb.vue'
import contentSingleColumn from '@/components/columns/ContentSingleColumn.vue'
import courseParticipantCard from '@/components/course/CourseParticipantCard.vue'
import groupModal from '@/components/course/CourseGroupModal.vue'

import store from '@/Store'
import icon from 'vue-awesome/components/Icon'
import courseAPI from '@/api/course'
import groupAPI from '@/api/group'
import roleAPI from '@/api/role'
import participationAPI from '@/api/participation'

export default {
    name: 'CourseEdit',
    props: {
        cID: {
            required: true
        }
    },
    data () {
        return {
            course: {},
            originalCourse: {},
            participants: [],
            unenrolledStudents: [],
            groups: [],
            selectedSortOption: null,
            selectedFilterGroupOption: null,
            searchVariable: '',
            unenrolledLoaded: false,
            numTeachers: 0,
            roles: [],
            viewEnrolled: true,
            order: false
        }
    },
    watch: {
        participants: {
            handler: function (val, _) {
                this.numTeachers = val.filter(p => p.role === 'Teacher').length
            },
            deep: true
        }
    },
    created () {
        courseAPI.get(this.cID)
            .then(course => {
                this.course = course
                this.originalCourse = this.deepCopyCourse(course)
            })

        groupAPI.getAllFromCourse(this.cID)
            .then(groups => { this.groups = groups })

        roleAPI.getFromCourse(this.cID)
            .then(roles => { this.roles = roles })

        if (this.$hasPermission('can_view_course_users')) {
            roleAPI.getFromCourse(this.cID)
                .then(roles => { this.roles = roles })

            participationAPI.getEnrolled(this.cID)
                .then(users => { this.participants = users })
        }
    },
    methods: {
        formFilled () {
            return this.course.name && this.course.abbreviation && this.course.startdate && this.course.enddate
        },
        onSubmit () {
            if (this.formFilled()) {
                courseAPI.update(this.cID, this.course, {customSuccessToast: 'Successfully updated the course.'})
                    .then(course => {
                        this.course = course
                        this.originalCourse = this.deepCopyCourse(course)
                        store.clearCache()
                    })
            } else {
                this.$toasted.error('One or more required fields are empty.')
            }
        },
        deleteCourse () {
            if (confirm('Are you sure you want to delete ' + this.course.name + '?')) {
                courseAPI.delete(this.cID)
                    .then(response => { this.$router.push({name: 'Home'}) })
            }
        },
        deleteParticipantLocally (user) {
            this.participants = this.participants.filter(function (item) {
                return user.id !== item.id
            })
            if (this.unenrolledLoaded === true) {
                this.unenrolledStudents.push(user)
            }
        },
        addParticipantLocally (user) {
            this.unenrolledStudents = this.unenrolledStudents.filter(function (item) {
                return user.id !== item.id
            })
            user.role = 'Student'
            user.group = null
            this.participants.push(user)
        },
        createGroup (groupName) {
            this.groups.push({
                'name': groupName
            })
        },
        deleteGroup (groupName) {
            groupAPI.getAllFromCourse(this.cID)
                .then(groups => { this.groups = groups })

            // TODO replace api function with frontend function
            if (this.$hasPermission('can_view_course_users')) {
                participationAPI.getEnrolled(this.cID)
                    .then(users => { this.participants = users })
            }
        },
        updateGroup (oldGroupName, newGroupName) {
            // TODO replace api function with frontend function
            groupAPI.getAllFromCourse(this.cID)
                .then(groups => { this.groups = groups })

            if (this.$hasPermission('can_view_course_users')) {
                participationAPI.getEnrolled(this.cID)
                    .then(users => { this.participants = users })
            }
        },
        loadUnenrolledStudents () {
            participationAPI.getUnenrolled(this.cID)
                .then(users => { this.unenrolledStudents = users })
            this.unenrolledLoaded = !this.unenrolledLoaded
        },
        routeToEditCourseRoles () {
            this.$router.push({
                name: 'UserRoleConfiguration',
                params: { cID: this.cID }
            })
        },
        compare (a, b) {
            if (a < b) { return this.order ? 1 : -1 }
            if (a > b) { return this.order ? -1 : 1 }
            return 0
        },
        toggleOrder () {
            this.order = !this.order
        },
        toggleEnroled () {
            this.viewEnrolled = !this.viewEnrolled
        },
        deepCopyCourse (course) {
            var copyCourse = {
                name: course.name, abbreviation: course.abbreviation, startdate: course.startdate, enddate: course.enddate
            }

            return copyCourse
        },
        checkChanged () {
            if (this.course.name !== this.originalCourse.name ||
                    this.course.abbreviation !== this.originalCourse.abbreviation ||
                    this.course.startdate !== this.originalCourse.startdate ||
                    this.course.enddate !== this.originalCourse.enddate) {
                return true
            }

            return false
        },
        updateParticipants (val, uID) {
            for (var i = 0; i < this.participants.length; i++) {
                if (uID === this.participants[i].id) {
                    this.participants[i].role = val
                }
            }
            this.numTeachers = this.participants.filter(p => p.role === 'Teacher').length
        }
    },
    computed: {
        filteredUsers () {
            let self = this

            function compareFullName (a, b) {
                return self.compare(a.name, b.name)
            }

            function compareUsername (a, b) {
                return self.compare(a.username, b.username)
            }

            function searchFilter (user) {
                var username = user.username.toLowerCase()
                var fullName = user.first_name.toLowerCase() + ' ' + user.last_name.toLowerCase()
                var searchVariable = self.searchVariable.toLowerCase()

                return username.includes(searchVariable) ||
                       fullName.includes(searchVariable)
            }

            function groupFilter (user) {
                if (self.selectedFilterGroupOption) {
                    if (!user.group) {
                        return user.group === self.selectedFilterGroupOption
                    } else {
                        return user.group.includes(self.selectedFilterGroupOption)
                    }
                }

                return true
            }

            var viewList = this.participants

            /* Switch view list with drop down menu and load unenrolled
               students when accessing other students at first time. */
            if (!this.viewEnrolled) {
                if (this.unenrolledLoaded === false) {
                    this.loadUnenrolledStudents()
                }
                viewList = this.unenrolledStudents
            }

            /* Filter list based on search input. */
            if (this.selectedSortOption === 'sortFullName') {
                viewList = viewList.sort(compareFullName)
            } else if (this.selectedSortOption === 'sortUsername') {
                viewList = viewList.sort(compareUsername)
            }

            return viewList.filter(searchFilter).filter(groupFilter)
        }
    },
    components: {
        'add-user-card': addUsersToCourseCard,
        'bread-crumb': breadCrumb,
        'content-single-column': contentSingleColumn,
        'course-participant-card': courseParticipantCard,
        'group-modal': groupModal,
        icon
    },
    beforeRouteLeave (to, from, next) {
        if (this.checkChanged() && !confirm('Unsaved changes will be lost if you leave. Do you wish to continue?')) {
            next(false)
            return
        }

        next()
    }
}
</script>
