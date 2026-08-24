import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { describe, expect, it, beforeEach } from 'vitest';

import { GanttComponent } from './gantt.component';
import { TimelineService } from '@/services/timeline.service';

describe('GanttComponent', () => {
  let component: GanttComponent;
  let fixture: ComponentFixture<GanttComponent>;

  const timelineServiceMock = {
    yearMonthMaps: signal([
      {
        year: 2020,
        months: [10, 12],
      },
      {
        year: 2021,
        months: [1, 2],
      },
    ]),

    birthdays: signal([
      {
        name: 'Alice',
        year: 2020,
        month: 10,
        day: 10,
      },
    ]),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GanttComponent],
      providers: [
        {
          provide: TimelineService,
          useValue: timelineServiceMock,
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(GanttComponent);

    component = fixture.componentInstance;

    fixture.componentRef.setInput('monthTabWidth', 100);
    fixture.componentRef.setInput('playlistTabWidth', 50);
    fixture.componentRef.setInput('lineGapX', 10);
    fixture.componentRef.setInput('lineGapY', 20);
    fixture.componentRef.setInput('legendMarginTop', 5);

    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });

  describe('infoGant', () => {
    it('ガント情報を作成する', () => {
      const result = component.infoGant();

      expect(result).toHaveLength(1);
      expect(result[0].name).toBe('Alice');
      expect(result[0].gant.length).toBeGreaterThan(0);
    });

    it('年齢ラベルを正しく作成する', () => {
      const result = component.infoGant();

      expect(result[0].gant[0].label).toBe('Alice 0歳');
      expect(result[0].gant[1].label).toBe('Alice 1歳');
    });
  });

  describe('getLinePosition', () => {
    it('ガントの線の位置を計算する', () => {
      const result = component.getLinePosition(2, 5, 3);

      expect(result).toEqual({
        width: '290px',
        marginLeft: '250px',
        marginTop: '60px',
      });
    });

    it('x2が負の場合は最後の月までの位置を計算する', () => {
      const result = component.getLinePosition(1, -1, 2);

      expect(result).toEqual({
        width: '290px',
        marginLeft: '150px',
        marginTop: '40px',
      });
    });
  });

  describe('getLegendPosition', () => {
    it('ガントの凡例の位置を計算する', () => {
      const result = component.getLegendPosition(2, 5, 3);

      expect(result).toEqual({
        width: '290px',
        marginLeft: '250px',
        marginTop: '65px',
      });
    });
  });
});