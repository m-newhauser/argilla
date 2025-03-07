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
  <a
    v-if="href"
    :class="buttonClasses"
    :href="href"
    :loading="loading"
    :disabled="disabled"
    :target="target"
    :rel="newRel"
    @click="onClick"
  >
    <slot />
  </a>

  <nuxt-link
    v-else-if="to"
    :class="buttonClasses"
    :to="to"
    :loading="loading"
    :disabled="disabled"
    @click="onClick"
  >
    <slot />
  </nuxt-link>

  <button
    v-else
    :class="buttonClasses"
    :tabindex="tabIndex"
    :loading="loading"
    :type="type"
    :disabled="disabled"
    @click="onClick"
  >
    <slot />
  </button>
</template>

<script>
export default {
  name: "BaseButton",
  props: {
    tabIndex: {
      type: Number,
      default: 0,
    },
    href: String,
    target: String,
    rel: String,
    type: {
      type: String,
      default: "button",
    },
    loading: Boolean,
    disabled: Boolean,
    centered: Boolean,
    to: { type: String | Object },
  },
  computed: {
    newRel() {
      if (this.target === "_blank") {
        return this.rel || "noopener";
      }

      return this.rel;
    },
    buttonClasses() {
      return {
        button: true,
        loading: this.loading,
        centered: this.centered,
      };
    },
  },
  methods: {
    onClick($event) {
      //FIXME - replace "click" event by "on-click"
      this.$emit("click", $event);
      this.$emit("on-click", $event);
    },
  },
};
</script>

<style lang="scss" scoped>
// buttons
%button {
  position: relative;
  display: flex;
  align-items: center;
  gap: $base-space;
  min-width: auto;
  overflow: hidden;
  user-select: none;
  outline: 0;
  background: none;
  border: 0;
  border-radius: $button-radius;
  font-style: inherit;
  font-variant: inherit;
  letter-spacing: inherit;
  font-weight: 500;
  text-align: center;
  text-decoration: none;
  white-space: nowrap;
  @include font-size(14px);
  line-height: 14px;
  padding: 12px 24px;
  transition: all 0.4s $cb-normal;
  cursor: pointer;
  &[disabled] {
    opacity: 0.5;
    cursor: default;
    pointer-events: none;
  }
  &:focus {
    outline: 2px solid $primary-color;
  }
  &:focus:not(:focus-visible) {
    outline: none;
  }
}
.button {
  @extend %button;
}
.small {
  @include font-size(13px);
  line-height: 13px;
  padding: $base-space;
}
.full-width {
  width: 100%;
  justify-content: center;
}
.primary {
  background-color: $primary-color;
  color: palette(white);
  .svg-icon {
    fill: palette(white);
  }
  &:hover,
  &:active,
  &.active {
    background-color: $primary-darken-color;
  }
  &.outline {
    background: none;
    border: 1px solid $primary-color;
    color: $primary-color;
    .svg-icon {
      fill: $primary-color;
    }
    &:hover,
    &:active,
    &.active {
      color: $primary-darken-color;
      border-color: $primary-darken-color;
    }
  }
  &.light {
    background: lighten($black-4, 50%);
    color: $primary-color;
    &:hover,
    &:active,
    &.active {
      background: $black-4;
    }
  }
  &.text {
    padding-left: 0;
    padding-right: 0;
    background: none;
    color: $primary-color;
    &:hover {
      background: none;
      color: darken($primary-color, 10%);
    }
  }
  &.link {
    background: none;
    color: $primary-color;
    &:hover {
      text-decoration: underline;
      background: none;
    }
  }
}

.secondary {
  background-color: palette(grey, 600);
  color: palette(grey, 200);
  .svg-icon {
    fill: palette(grey, 200);
  }
  &:hover,
  &:active,
  &.active {
    background-color: darken(palette(grey, 600), 5%);
  }
  &.outline {
    background: none;
    border: 1px solid $black-54;
    color: palette(grey, 200);
  }
  &.light {
    background: lighten($black-4, 50%);
    color: $black-54;
    &:hover,
    &:active,
    &.active {
      background: $black-4;
    }
    .svg-icon {
      fill: $black-54;
    }
  }

  &.text {
    padding-left: 0;
    padding-right: 0;
    background: none;
    color: $black-54;
    &:hover {
      background: none;
      color: $black-87;
    }
  }
  &.link {
    background: none;
    color: $black-54;
    padding: 0;
    &:hover {
      text-decoration: underline;
      background: none;
    }
  }
}
.--danger {
  background-color: $danger;
  color: palette(white);
  .svg-icon {
    fill: palette(white);
  }
  &:hover,
  &:active,
  &.active {
    background-color: darken($danger, 10%);
  }
  &.outline {
    background: none;
    border: 1px solid $danger;
    color: $danger;
    .svg-icon {
      fill: $danger;
    }
    &:hover,
    &:active,
    &.active {
      color: darken($danger, 10%);
      border-color: darken($danger, 10%);
    }
  }
  &.light {
    background: lighten($black-4, 50%);
    color: $danger;
    &:hover,
    &:active,
    &.active {
      background: $black-4;
    }
  }
  &.link {
    background: none;
    color: $danger;
    &:hover {
      text-decoration: underline;
      background: none;
    }
  }
}
.clear {
  background: none;
  height: 30px;
  &:hover,
  &:active,
  &.active {
    background: $black-4;
  }
}
</style>
