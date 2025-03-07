<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <transition appear name="fade">
    <div class="table-info">
      <div class="table-info__header">
        <slot name="columns">
          <div class="table-info__item">
            <div
              v-for="(column, key) in columns"
              :key="key"
              class="table-info__item__col"
            >
              <lazy-table-filtrable-column
                :column="column"
                :data="data"
                :filters="filters"
                v-if="column.filtrable"
                @applyFilters="onApplyFilters"
              />
              <button
                v-else-if="column.sortable"
                :data-title="column.tooltip"
                :class="[sortOrder, { active: sortedBy === column.field }]"
                @click="sort(column)"
              >
                <svgicon width="18" height="18" color="#4D4D4D" name="sort" />
                <span>{{ column.name }}</span>
              </button>
              <button v-else :data-title="column.tooltip">
                <span>{{ column.name }}</span>
              </button>
            </div>
          </div>
        </slot>
      </div>
      <results-empty v-if="tableIsEmpty" :title="emptySearchInfo.title" />
      <template v-else>
        <div class="table-info__body">
          <ul>
            <li v-for="item in filteredResults" :key="String(item.id)">
              <div class="table-info__item">
                <base-checkbox
                  v-if="globalActions"
                  v-model="item.selectedRecord"
                  class="list__item__checkbox"
                  :value="item.name"
                  @change="onCheckboxChanged($event, item.id)"
                />
                <span
                  v-for="(column, idx) in columns"
                  :key="idx"
                  class="table-info__item__col"
                >
                  <span :class="column.class">
                    <a
                      v-if="column.type === 'action'"
                      href="#"
                      @click.prevent="onActionClicked(item.kind, item)"
                      >{{ itemValue(item, column) }}
                    </a>
                    <span v-else-if="column.type === 'link'">
                      <nuxt-link v-if="item.link" :to="item.link"
                        >{{ itemValue(item, column) }}
                      </nuxt-link>
                      <span v-else>{{ itemValue(item, column) }}</span>
                      <base-action-tooltip tooltip="Copied">
                        <base-button
                          title="Copy to clipboard"
                          class="table-info__actions__button button-icon"
                          @click.prevent="onActionClicked('copy-name', item)"
                        >
                          <svgicon name="copy" width="16" height="16" />
                        </base-button>
                      </base-action-tooltip>
                    </span>
                    <base-date
                      format="date-relative-now"
                      v-else-if="column.type === 'date'"
                      :date="itemValue(item, column)"
                    />
                    <span v-else-if="column.type === 'number'">
                      {{ itemValue(item, column) | formatNumber }}
                    </span>
                    <span
                      v-else-if="
                        !isNaN(itemValue(item, column)) &&
                        column.type === 'percentage'
                      "
                    >
                      {{ itemValue(item, column) | percent }}
                    </span>
                    <span v-else-if="column.type === 'array'">
                      <p
                        v-for="(arrayItem, index) in itemValue(item, column)"
                        :key="index"
                      >
                        {{ arrayItem
                        }}{{
                          index + 1 === itemValue(item, column).length
                            ? ""
                            : ","
                        }}
                      </p>
                    </span>
                    <span v-else-if="column.type === 'object'">
                      <p
                        v-for="key in Object.keys(itemValue(item, column))"
                        :key="key"
                      >
                        <strong>{{ key }}:</strong>
                        {{ itemValue(item, column)[key] }}
                      </p>
                    </span>
                    <!-- TODO: remove references to task -->
                    <span v-else-if="column.type === 'task'">
                      {{ itemValue(item, column) }}
                    </span>
                    <span v-else>{{ itemValue(item, column) }}</span>
                  </span>
                </span>
                <div v-if="visibleActions" class="table-info__actions">
                  <base-action-tooltip
                    v-for="action in filterActions"
                    :key="action.index"
                    :tooltip="action.tooltip"
                  >
                    <base-button
                      :title="action.title"
                      class="table-info__actions__button button-icon"
                      @click="onActionClicked(action.name, item)"
                    >
                      <svgicon
                        v-if="action.icon !== undefined"
                        :name="action.icon"
                        width="16"
                        height="16"
                      />
                    </base-button>
                  </base-action-tooltip>
                </div>
                <base-modal
                  v-if="!!deleteModalContent"
                  :modal-custom="true"
                  :prevent-body-scroll="true"
                  modal-class="modal-secondary"
                  :modal-title="deleteModalContent.title"
                  :modal-visible="visibleModalId === item.id"
                  @close-modal="$emit('close-modal')"
                >
                  <div>
                    <p v-html="deleteModalContent.text"></p>
                    <div class="modal-buttons">
                      <base-button
                        class="primary outline"
                        @click="$emit('close-modal')"
                      >
                        Cancel
                      </base-button>
                      <base-button
                        class="primary"
                        @click="onActionClicked('confirm-delete', item)"
                      >
                        Yes, delete
                      </base-button>
                    </div>
                  </div>
                </base-modal>
              </div>
            </li>
          </ul>
        </div>
      </template>
    </div>
  </transition>
</template>

<script>
import "assets/icons/trash-empty";
import "assets/icons/refresh";
import "assets/icons/copy";
import "assets/icons/settings";
import "assets/icons/link";
import "assets/icons/sort";
export default {
  props: {
    data: {
      type: Array,
      default: () => [],
    },
    actions: {
      type: Array,
      default: () => [],
    },
    columns: Array,
    searchOn: {
      type: String,
      default: undefined,
    },
    sortedOrder: {
      type: String,
      default: "desc",
    },
    sortedByField: {
      type: String,
      default: undefined,
    },
    noDataInfo: {
      title: undefined,
      message: undefined,
      icon: undefined,
    },
    emptySearchInfo: {
      title: undefined,
    },
    hideButton: {
      type: Boolean,
      default: false,
    },
    visibleModalId: {
      type: String | Array,
      default: undefined,
    },
    deleteModalContent: {
      type: Object,
    },
    globalActions: {
      type: Boolean,
      default: true,
    },
    querySearch: {
      type: String,
      default: undefined,
    },
    activeFilters: {
      type: Array,
      default: () => {
        return [];
      },
    },
  },
  data() {
    return {
      sortOrder: this.sortedOrder,
      visibleActions: true,
      sortedBy: this.sortedByField,
      allRecordsSelected: false,
      selectedItems: [],
      filters: {},
    };
  },
  computed: {
    tableIsEmpty() {
      return this.filteredResults && this.filteredResults.length === 0;
    },
    filterActions() {
      return this.actions.filter((a) => a.hide !== this.hideButton);
    },
    filteredResults() {
      const matchSearch = (item) => {
        if (this.querySearch === undefined) {
          return true;
        }
        const querySearch = this.querySearch.toLowerCase();
        if (this.searchOn) {
          return item[this.searchOn]
            .toString()
            .toLowerCase()
            .includes(querySearch);
        }
        return false;
      };
      const matchFilters = (item) => {
        if (this.filters) {
          return Object.keys(this.filters).every((key) => {
            if (this.isObject(item[key])) {
              return this.filters[key].find(
                (filter) => filter.value === item[key][filter.key]
              );
            }

            return this.filters[key].includes(item[key]);
          });
        }

        return true;
      };
      const itemComparator = (a, b) => {
        const modifier = this.sortedOrder === "desc" ? -1 : 1;

        if (a[this.sortedBy] < b[this.sortedBy]) return -1 * modifier;
        if (a[this.sortedBy] > b[this.sortedBy]) return 1 * modifier;

        return 0;
      };
      const results = this.data.filter(matchSearch).filter(matchFilters);
      return results.sort(itemComparator);
    },
  },
  beforeMount() {
    this.sortedBy = this.sortedByField;
    const appliedFilters = this.activeFilters.filter(
      (filter) => filter.values.length
    );
    appliedFilters?.forEach(({ column, values }) => {
      this.$set(this.filters, column, values);
    });
  },
  methods: {
    isObject(obj) {
      return Object.prototype.toString.call(obj) === "[object Object]";
    },
    itemValue(item, column) {
      if (column.subfield) {
        return item[column.field][column.subfield];
      }
      return item[column.field];
    },
    onActionClicked(action, item) {
      this.$emit("onActionClicked", action, item);
    },
    sort(column) {
      this.$emit("sort-column", column.field, this.sortOrder);
      this.sortedBy = column.field;
      if (column.field === this.sortedBy) {
        this.sortOrder = this.sortOrder === "asc" ? "desc" : "asc";
      }
    },
    onApplyFilters(column, selectedOptions) {
      if (selectedOptions.length) {
        this.$set(this.filters, column.field, selectedOptions);
      } else {
        this.$delete(this.filters, column.field);
      }
      this.$emit("filter-applied", {
        column: column.field,
        values: selectedOptions,
      });
    },
    selectAll(value) {
      this.onAllCheckboxChanged(value);
    },
    onAllCheckboxChanged(value) {
      this.filteredResults.forEach((record) => {
        record.selectedRecord = value;
      });

      this.selectedItems = this.filteredResults.filter(
        (filtered) => filtered.selectedRecord === true
      );
    },
    onCheckboxChanged(value, id) {
      this.filteredResults.forEach((record) => {
        if (record.id === id) {
          record.selectedRecord = value;
        }
      });

      this.selectedItems = this.filteredResults.filter(
        (filtered) => filtered.selectedRecord === true
      );

      this.allRecordsSelected =
        this.filteredResults.length === this.selectedItems.length;
    },
  },
};
</script>

<style lang="scss" scoped>
.table-info {
  $this: &;
  padding: 0;
  list-style: none;
  margin-bottom: 5em;
  color: $black-54;
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  &__header {
    background: palette(white);
    min-height: 50px;
    position: relative;
    margin-top: $base-space * 2;
    &__checkbox {
      margin: 0 !important;
    }
    &__button {
      position: absolute !important;
      top: 2em;
      right: 2em;
      margin-bottom: 0 !important;
    }
    #{$this}__item {
      min-height: 50px;
      background: none;
      padding-top: 0.2em;
      padding-bottom: 0.2em;
      display: flex;
      align-items: center;
    }
    button:not(.button) {
      cursor: pointer;
      border: 0;
      outline: none;
      background: transparent;
      padding-left: 0;
      padding-right: 0;
      color: $black-87;
      @include font-size(14px);
      text-align: left;
      display: flex;
      align-items: center;
      @include media("<=desktop") {
        display: block;
        .svg-icon {
          display: block;
        }
      }
      span {
        white-space: nowrap;
      }
    }
  }
  &__body {
    overflow: auto;
    height: calc(100vh - 203px);
    padding-bottom: 0.5em;
    @extend %hide-scrollbar;
    #{$this}__item {
      margin-bottom: -1px;
      &:hover,
      &:focus {
        background: #fcfcfc;
      }
    }
  }
  &__item {
    background: palette(white);
    position: relative;
    list-style: none;
    padding: 2em 5em 2em 2em;
    display: flex;
    width: 100%;
    align-items: flex-start;
    text-decoration: none;
    outline: none;
    border: 1px solid palette(grey, 700);
    &__col {
      text-align: left;
      margin-right: 1em;
      flex: 1 1 0px;
      &:nth-last-of-type(-n + 1) {
        max-width: 120px;
      }
      &:first-child {
        width: auto;
        min-width: auto;
        flex-grow: 1.5;
      }
    }
    .svg-icon {
      margin-right: $base-space;
      fill: $black-54;
      &:hover {
        fill: $black-87;
      }
    }
  }
  &__tag {
    background: palette(grey, 100);
    display: inline-block;
    border-radius: $border-radius-s;
    color: palette(white);
    @include font-size(12px);
    box-shadow: 0 1px 4px 1px rgba(222, 222, 222, 0.5);
    padding: 0.1em 0.5em;
    margin-left: 1em;
  }
  .empty {
    margin-top: 5em;
    height: auto;
  }
  &__actions {
    position: absolute;
    right: 2em;
    &__button {
      position: relative;
      margin-left: 1em;
      padding: 0 !important;
      display: inline-block;
      .svg-icon {
        margin: 0;
      }
      & + #{$this} {
        margin-left: auto;
      }
    }
  }
  &__title {
    display: block;
    hyphens: auto;
    word-break: break-word;
    .button-icon {
      padding: $base-space;
      margin-left: $base-space;
      display: inline-block;
      .svg-icon {
        margin: 0;
      }
    }
    a {
      text-decoration: none;
      &:hover {
        color: palette(black);
      }
    }
  }
  .text {
    color: $black-54;
    p {
      display: inline-block;
      background: palette(grey, 800);
      padding: 0.5em;
      border-radius: 10px;
      margin-right: 0.5em;
      margin-top: 0;
      hyphens: auto;
      word-break: break-word;
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
  .array {
    p {
      margin-top: 0;
      margin-bottom: 0;
      display: inline;
      hyphens: auto;
      word-break: break-word;
    }
  }
}
button[data-title] {
  position: relative;
  @extend %has-tooltip--top;
  @extend %tooltip-large-text;
}
</style>
