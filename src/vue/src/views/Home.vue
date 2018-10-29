<template>
    <content-columns>
        <bread-crumb slot="main-content-column" :currentPage="'Courses'" @edit-click="handleEdit()"/>

        <div v-for="c in courses" :key="c.id" slot="main-content-column">
            <b-link :to="{ name: 'Course', params: { cID: c.id, courseName: c.name } }">
                <main-card
                    :line1="c.name"
                    :line2="c.startdate ? (c.startdate.substring(0, 4) + (c.enddate ? ' - ' + c.enddate.substring(0, 4) : '')) : ''"
                    :color="$root.getBorderClass(c.id)" />
            </b-link>
        </div>
        <b-button v-if="$hasPermission('can_add_course')"
            slot="main-content-column"
            class="add-button grey-background full-width"
            @click="showModal('createCourseRef')">
            <icon name="plus"/>
            Create New Course
        </b-button>

        <h3 slot="right-content-column">To Do</h3>
        <deadline-deck slot="right-content-column" :deadlines="deadlines"/>

        <b-modal
            slot="main-content-column"
            ref="editCourseRef"
            title="Global Changes"
            size="lg"
            hide-footer>
                <edit-home @handleAction="handleConfirm('editCourseRef')"></edit-home>
        </b-modal>

        <b-modal
            slot="main-content-column"
            ref="createCourseRef"
            title="New Course"
            size="lg"
            hide-footer>
                <create-course @handleAction="handleConfirm('createCourseRef')"></create-course>
        </b-modal>
    </content-columns>
</template>

<script>
import contentColumns from '@/components/columns/ContentColumns.vue'
import breadCrumb from '@/components/assets/BreadCrumb.vue'
import mainCard from '@/components/assets/MainCard.vue'
import todoCard from '@/components/assets/TodoCard.vue'
import createCourse from '@/components/course/CreateCourse.vue'
import editHome from '@/components/home/EditHome.vue'
import deadlineDeck from '@/components/assets/DeadlineDeck.vue'

import courseAPI from '@/api/course'
import assignmentAPI from '@/api/assignment'

import icon from 'vue-awesome/components/Icon'

export default {
    name: 'Home',
    data () {
        return {
            intituteName: 'Universiteit van Amsterdam (UvA)',
            courses: [],
            deadlines: []
        }
    },
    components: {
        'content-columns': contentColumns,
        'bread-crumb': breadCrumb,
        'main-card': mainCard,
        'todo-card': todoCard,
        'create-course': createCourse,
        'edit-home': editHome,
        'deadline-deck': deadlineDeck,
        icon
    },
    created () {
        this.loadCourses()

        assignmentAPI.getUpcoming()
            .then(deadlines => { this.deadlines = deadlines })
    },
    methods: {
        loadCourses () {
            courseAPI.getUserEnrolled()
                .then(courses => { this.courses = courses })
        },
        showModal (ref) {
            this.$refs[ref].show()
        },
        handleConfirm (ref) {
            if (ref === 'createCourseRef') {
                this.loadCourses()
            }

            this.hideModal(ref)
        },
        handleEdit () {
            // TODO: Open EditHome
        },
        hideModal (ref) {
            this.$refs[ref].hide()
        }
    }
}
</script>
