<!--
    Breadcrumb vue component
    Breadcrumb mirrors the current router link
    Caches named view names in store
    Settings object allows aliasing of page names and creation of new named routes
-->

<template>
    <div class="breadcrumb-container">
        <b-button v-if="canEdit()" @click="editClick()" class="float-right change-button multi-form">
            <icon name="edit"/>
            Edit
        </b-button>
        <div>
            <h4 v-if="crumbs.length > 1">
                <span v-for="crumb in crumbs.slice(0, -1)" :key="crumb.route">
                    <b-link tag="b-button" :to="{ name: crumb.routeName }">{{ crumb.displayName }}</b-link> /
                </span>
            </h4>
            <h1>
                {{ crumbs.slice(-1)[0].displayName }}
            </h1>
        </div>
    </div>
</template>

<script>
import icon from 'vue-awesome/components/Icon'
import store from '@/Store.vue'

import commonAPI from '@/api/common'

export default {
    components: {
        icon
    },
    /*
        aliases: aliases for unnamed vews
        namedViews: list of named views, with associated data field in get_names and primary parameter
    */
    data () {
        return {
            settings: {
                aliases: {
                    'Home': 'Courses',
                    'FormatEdit': 'Format Editor',
                    'CourseEdit': 'Course Editor',
                    'AssignmentsOverview': 'Assignments',
                    'UserRoleConfiguration': 'User Role Configuration'
                },
                namedViews: {
                    'Course': { apiReturnValue: 'course', primaryParam: 'cID' },
                    'Assignment': { apiReturnValue: 'assignment', primaryParam: 'aID' },
                    'Journal': { apiReturnValue: 'journal', primaryParam: 'jID' }
                }
            },
            cachedMap: {},
            crumbs: []
        }
    },
    methods: {
        // Match routes that prepend the current path, create incomplete crumbs
        findRoutes () {
            var routeMatched = this.$route.matched[0].path
            var routerRoutes = this.$router.options.routes
            routerRoutes.sort((a, b) => a.path.length - b.path.length)

            // Add every matched (sub)route with params substituted to use as key
            for (var route of routerRoutes.slice(1)) {
                if (routeMatched.startsWith(route.path)) {
                    var fullpath = route.path
                    for (var kvpair of Object.entries(this.$route.params)) {
                        fullpath = fullpath.replace(':' + kvpair[0], kvpair[1])
                    }
                    this.crumbs.push({ route: fullpath, routeName: route.name, displayName: null })
                }
            }
        },
        // Load the displayname map from cache, complete crumbs from cache where possible, do aliasing
        addDisplayNames () {
            this.cachedMap = store.state.cachedMap

            for (var crumb of this.crumbs) {
                if (!this.settings.namedViews[crumb.routeName]) {
                    crumb.displayName = this.settings.aliases[crumb.routeName] || crumb.routeName
                } else {
                    crumb.displayName = this.cachedMap[crumb.route] || null
                }
            }
        },
        // If any are still missing display names (not in cache), request the names and set them in cache
        fillCache () {
            var crumbsMissingDisplayName = this.crumbs.filter(crumb => !crumb.displayName)

            // Incrementally build request
            var request = {}
            for (var crumb of crumbsMissingDisplayName) {
                var paramName = this.settings.namedViews[crumb.routeName].primaryParam
                request[paramName] = this.$route.params[paramName]
            }

            if (crumbsMissingDisplayName.length > 0) {
                commonAPI.getNames(request)
                    .then(names => {
                        for (var crumb of crumbsMissingDisplayName) {
                            crumb.displayName = names[this.settings.namedViews[crumb.routeName].apiReturnValue]
                            this.cachedMap[crumb.route] = crumb.displayName
                        }
                    })
                    .then(_ => { store.setCachedMap(this.cachedMap) })
            }
        },
        editClick () {
            this.$emit('edit-click')
        },
        canEdit () {
            var pageName = this.$route.name

            if ((pageName === 'Home' && this.$hasPermission('can_edit_institute_details')) ||
               (pageName === 'Course' && this.$hasPermission('can_edit_course_details')) ||
               (pageName === 'Assignment' && this.$hasPermission('can_edit_assignment'))) {
                return true
            }
        }
    },
    created () {
        this.findRoutes()
        this.addDisplayNames()
        this.fillCache()
    }
}
</script>

<style lang="sass">
.breadcrumb-container
    padding-right: 10px
</style>
