<template>
    <content-single-column>
        <bread-crumb :currentPage="'Assignments'"></bread-crumb>

        <b-card class="no-hover">
            <input class="theme-input full-width multi-form" type="text" v-model="searchVariable" placeholder="Search..."/>
            <div class="d-flex">
                <b-form-select class="multi-form mr-2" v-model="selectedSortOption" :select-size="1">
                   <option>Sort by...</option>
                   <option value="sortDate">Sort by date</option>
                   <option value="sortName">Sort by name</option>
                   <option v-if="$hasPermission('can_add_course')"
                           value="sortNeedsMarking">Sort by marking needed</option>
                </b-form-select>
                <b-button v-on:click.stop v-if="!order" @click="toggleOrder" class="button multi-form">
                    <icon name="long-arrow-down"/>
                    Ascending
                </b-button>
                <b-button v-on:click.stop v-if="order" @click="toggleOrder" class="button multi-form">
                    <icon name="long-arrow-up"/>
                    Descending
                </b-button>
            </div>
        </b-card>

        <div v-for="(d, i) in computedDeadlines" :key="i">
            <b-link tag="b-button" :to="assignmentRoute(d.course.id, d.id, d.journal)">
                <todo-card :deadline="d"/>
            </b-link>
        </div>
    </content-single-column>
</template>

<script>
import contentSingleColumn from '@/components/columns/ContentSingleColumn.vue'
import breadCrumb from '@/components/assets/BreadCrumb.vue'
import mainCard from '@/components/assets/MainCard.vue'
import todoCard from '@/components/assets/TodoCard.vue'

import icon from 'vue-awesome/components/Icon'
import assignmentAPI from '@/api/assignment'

export default {
    name: 'AssignmentsOverview',
    data () {
        return {
            deadlines: [],
            selectedSortOption: 'sortDate',
            searchVariable: '',
            order: false
        }
    },
    created () {
        assignmentAPI.getUpcoming()
            .then(deadlines => { this.deadlines = deadlines })
            .catch(error => { this.$toasted.error(error.response.data.description) })
    },
    components: {
        'content-single-column': contentSingleColumn,
        'bread-crumb': breadCrumb,
        'main-card': mainCard,
        icon,
        'todo-card': todoCard
    },
    methods: {
        assignmentRoute (cID, aID, jID) {
            var route = {
                name: 'Assignment',
                params: {
                    cID: cID,
                    aID: aID
                }
            }

            if (this.$hasPermission('can_view_all_journals', 'assignment', aID)) {
                route.name = 'Assignment'
                return route
            }

            route.name = 'Journal'
            route.params.jID = jID
            return route
        },
        compare (a, b) {
            if (a < b) { return this.order ? 1 : -1 }
            if (a > b) { return this.order ? -1 : 1 }
            return 0
        },
        toggleOrder () {
            this.order = !this.order
        }
    },
    computed: {
        computedDeadlines: function () {
            let self = this

            function compareName (a, b) {
                return self.compare(a.name, b.name)
            }

            function compareDate (a, b) {
                return self.compare(new Date(a.deadline), new Date(b.deadline))
            }

            function compareMarkingNeeded (a, b) {
                return self.compare(a.stats.needs_marking + a.stats.unpublished, b.stats.needs_marking + b.stats.unpublished)
            }

            function searchFilter (assignment) {
                var searchVariable = self.searchVariable.toLowerCase()
                return assignment.name.toLowerCase().includes(searchVariable) ||
                       assignment.course.abbreviation.toLowerCase().includes(searchVariable)
            }

            if (this.selectedSortOption === 'sortName') {
                return this.deadlines.filter(searchFilter).slice().sort(compareName)
            } else if (this.selectedSortOption === 'sortDate') {
                return this.deadlines.filter(searchFilter).slice().sort(compareDate)
            } else if (this.selectedSortOption === 'sortNeedsMarking') {
                return this.deadlines.filter(searchFilter).slice().sort(compareMarkingNeeded)
            } else {
                return this.deadlines.filter(searchFilter).slice()
            }
        }
    }
}
</script>
