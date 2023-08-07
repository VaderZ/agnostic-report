import { NavigationFailure, RouteLocationNormalizedLoaded, Router, useRoute, useRouter } from 'vue-router'
import moment from 'moment'

export interface GenericJSONResponse {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [prop: string]: any
}

export function getShortUpdateInterval(): number {
  return 10 * 1000 + Math.ceil(Math.random() * 1000)
}

export function getLongUpdateInterval(): number {
  return 60 * 1000 + Math.ceil(Math.random() * 1000)
}

export function getTestColorByResult(result: string): string | undefined {
  return {
    passed: '#97cc64',
    failed: '#fd5a3e',
    xpassed: '#ffd050',
    xfailed: '#d35ebe',
    skipped: '#aaa',
    unknown: '#c1946a',
  }[result]
}

export function getProgressColorByLevel(level: string): string | undefined {
  return {
    INFO: '#97cc64',
    ERROR: '#fd5a3e',
    WARNING: '#ffd050',
  }[level]
}

export function formatByteSize(bs: number): string {
  if (bs > Math.pow(1024, 3)) {
    return `${(Math.ceil((bs / Math.pow(1024, 3)) * 10.0) / 10).toLocaleString(undefined, {
      minimumFractionDigits: 1,
    })}G`
  }
  if (bs > Math.pow(1024, 2)) {
    return `${(Math.ceil((bs / Math.pow(1024, 2)) * 10.0) / 10).toLocaleString(undefined, {
      minimumFractionDigits: 1,
    })}M`
  }
  if (bs > 1024) {
    return `${(Math.ceil((bs / 1024) * 10.0) / 10).toLocaleString(undefined, { minimumFractionDigits: 1 })}K`
  }
  return `${bs}B`
}

export function getIconByMime(mime: string): string {
  if (mime.startsWith('audio')) {
    return 'far-file-audio'
  }
  if (mime.endsWith('zip')) {
    return 'far-file-archive'
  }
  if (mime.startsWith('text/x-')) {
    return 'far-file-code'
  }
  if (mime.startsWith('text')) {
    return 'far-file-text'
  }
  if (mime.startsWith('image')) {
    return 'far-file-image'
  }
  if (mime.startsWith('video')) {
    return 'far-file-movie'
  }
  if (mime.indexOf('pdf') >= 0) {
    return 'far-file-pdf'
  }
  return 'far-file'
}

interface ParsedHash {
  [prop: string]: string
}

export class HashUtil {
  route: RouteLocationNormalizedLoaded = useRoute()
  router: Router = useRouter()

  parse(): ParsedHash {
    const parsed: ParsedHash = {}
    if (this.route.hash.length > 1) {
      const parts: string[] = this.route.hash.replace('#', '').split('&')
      for (const part of parts) {
        const keyVal: string[] = part.split('=')
        parsed[keyVal[0]] = keyVal[1]
      }
    }
    return parsed
  }

  dump(parsed: ParsedHash): string {
    const serialized: string[] = []
    for (const key in parsed) {
      serialized.push(`${key}=${parsed[key]}`)
    }
    return `#${serialized.join('&')}`
  }

  get(key: string): string {
    return this.parse()[key]
  }

  set(key: string, value: string): Promise<void | NavigationFailure | undefined> {
    const parsed = this.parse()
    parsed[key] = value
    return this.router.replace({ ...this.route, hash: this.dump(parsed) })
  }

  remove(key: string): Promise<void | NavigationFailure | undefined> {
    const parsed = this.parse()
    delete parsed[key]
    return this.router.replace({ ...this.route, hash: this.dump(parsed) })
  }
}

export function formatDate(date: string | number | undefined): string | undefined {
  if (date) {
    return moment(date).format('LLL')
  }
}

export function formatTime(date: string | number | undefined): string | undefined {
  if (date) {
    return moment(date).format('LTS')
  }
}

export function formatInterval(interval: string | number | undefined): string | undefined {
  if (interval) {
    return moment.utc(moment.duration(interval, 'seconds').asMilliseconds()).format('HH:mm:ss')
  }
}

export function getFormattedInterval(start: string, finish: string): string {
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  return moment.utc(moment(finish) - moment(start)).format('HH:mm:ss')
}

export function getModalSize() {
  return `${0.9 * window.innerWidth}px`
}

export function formatMetric(value: number | string, format: string): string | undefined {
  switch (format) {
    case 'float':
      return typeof value == 'number' ? value.toFixed(2) : ''
    case 'interval':
      return formatInterval(value)
    case 'date':
      return formatDate(value)
  }
}
