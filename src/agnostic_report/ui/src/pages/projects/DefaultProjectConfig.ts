export const defaultProjectConfig = {
  project: {
    tabs: [
      {
        name: 'Summary',
        layout: 'FourTopDoubleLeftDoubleRight',
        widgets: [
          {
            type: 'ProjectTestsOverTime',
          },
          {
            type: 'HTMLText',
            config: {
              html: '<div>' + '</div><h1>Project Description</h1><br/>' + '<p>Add some text here</p><br/></div>',
            },
          },
          {
            type: 'ProjectTopFailedTests',
            config: {
              count: 5,
            },
          },
          {
            type: 'HTMLText',
            config: {
              html: '<div>' + '</div><h1>Project Description</h1><br/>' + '<p>Add some text here</p><br/></div>',
            },
          },
        ],
      },
      {
        name: 'Test Runs',
        layout: 'FullPage',
        widgets: [
          {
            type: 'ProjectTestRunsList',
          },
        ],
      },
    ],
  },
  testrun: {
    tabs: [
      {
        name: 'Summary',
        layout: 'SixSingle',
        widgets: [
          {
            type: 'TestRunTestsByResult',
          },
          {
            type: 'HTMLText',
            config: {
              html: '<div>' + '</div><h1>Project Description</h1><br/>' + '<p>Add some text here</p><br/></div>',
            },
          },
        ],
      },
      {
        name: 'Tests',
        layout: 'FullPage',
        widgets: [
          {
            type: 'TestsRunTestsList',
          },
        ],
      },
      {
        name: 'Metrics',
        layout: 'FullPage',
        widgets: [
          {
            type: 'TestRunMetricsList',
          },
        ],
      },
      {
        name: 'Progress',
        layout: 'FullPage',
        widgets: [
          {
            type: 'TestRunProgress',
          },
        ],
      },
      {
        name: 'Logs',
        layout: 'FullPage',
        widgets: [
          {
            type: 'TestRunLogsList',
          },
        ],
      },
    ],
  },
}
